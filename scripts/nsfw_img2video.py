#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import torch
import imageio.v2 as imageio
from PIL import Image


def ensure_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def load_svd_pipeline(model_id: str, device: torch.device):
    try:
        from diffusers import StableVideoDiffusionPipeline
    except Exception as exc:
        raise RuntimeError(
            "diffusers is required. Install requirements from requirements-nsfw.txt"
        ) from exc

    dtype = torch.float16 if device.type in ("cuda", "mps") else torch.float32
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=dtype,
        variant="fp16" if dtype == torch.float16 else None,
    )
    pipe.enable_model_cpu_offload() if device.type == "cpu" else pipe.to(device)
    pipe.enable_vae_tiling()
    return pipe


def generate_base_image_via_webui(
    address: str,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    cfg: float,
    sampler: str,
    seed: int,
    model: str | None,
) -> Image.Image:
    # Local import to avoid hard dependency if user already has an image
    import base64
    import requests

    payload: dict[str, object] = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg,
        "sampler_name": sampler,
        "seed": seed,
        "restore_faces": False,
    }
    if model:
        payload.update(
            {
                "override_settings": {"sd_model_checkpoint": model},
                "override_settings_restore_afterwards": True,
            }
        )
    resp = requests.post(f"{address}/sdapi/v1/txt2img", json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("images"):
        raise RuntimeError("WebUI returned no image for text prompt")
    img_bytes = base64.b64decode(data["images"][0])
    return Image.open(io.BytesIO(img_bytes)).convert("RGB")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Create a short NSFW video from an input image using Stable Video Diffusion. "
            "Optionally first generate the image via Stable Diffusion WebUI."
        )
    )
    parser.add_argument("--image", type=Path, default=None, help="Path to input image (RGB)")
    parser.add_argument("--prompt", type=str, default=None, help="Prompt if generating base image via WebUI")
    parser.add_argument("--address", type=str, default="http://127.0.0.1:7860", help="WebUI base URL")
    parser.add_argument("--negative", type=str, default="(lowres, bad anatomy, watermark)")
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=640)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--sampler", type=str, default="DPM++ SDE Karras")
    parser.add_argument("--seed", type=int, default=-1)
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument(
        "--svd-model",
        type=str,
        default="stabilityai/stable-video-diffusion-img2vid-xt",
        help="Hugging Face model id for SVD",
    )
    parser.add_argument("--num-frames", type=int, default=25)
    parser.add_argument("--fps", type=int, default=7)
    parser.add_argument("--out", type=Path, default=Path("output_nsfw.mp4"))

    args = parser.parse_args()

    if args.image is None and not args.prompt:
        print("Provide --image or --prompt to generate base image via WebUI", file=sys.stderr)
        sys.exit(2)

    device = ensure_device()
    pipe = load_svd_pipeline(args.svd_model, device)

    if args.image is None:
        try:
            base_image = generate_base_image_via_webui(
                address=args.address,
                prompt=args.prompt,
                negative_prompt=args.negative,
                width=args.width,
                height=args.height,
                steps=args.steps,
                cfg=args.cfg,
                sampler=args.sampler,
                seed=args.seed,
                model=args.model,
            )
        except Exception as exc:
            print(f"Failed to generate base image via WebUI: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        if not args.image.exists():
            print(f"Image not found: {args.image}", file=sys.stderr)
            sys.exit(1)
        base_image = Image.open(args.image).convert("RGB")

    base_image = base_image.resize((args.width, args.height), Image.LANCZOS)

    with torch.autocast(device_type=device.type, enabled=device.type != "cpu"):
        result = pipe(
            base_image,
            decode_chunk_size=8,
            motion_bucket_id=127,
            noise_aug_strength=0.02,
            num_frames=args.num_frames,
        )

    frames = result.frames[0]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    imageio.mimsave(args.out, [Image.fromarray(f) for f in frames], fps=args.fps)
    print(f"Saved video -> {args.out}")


if __name__ == "__main__":
    main()

