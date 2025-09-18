#!/usr/bin/env python3
import argparse
import base64
import sys
from pathlib import Path
import requests


def generate_image(
    address: str,
    prompt: str,
    negative_prompt: str,
    width: int,
    height: int,
    steps: int,
    cfg_scale: float,
    sampler_name: str,
    seed: int,
    model: str | None,
    hr_scale: float | None,
    hr_upscaler: str | None,
    denoising_strength: float | None,
):
    payload: dict[str, object] = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "sampler_name": sampler_name,
        "seed": seed,
        "restore_faces": False,
    }

    if hr_scale and hr_scale > 1.0 and hr_upscaler:
        payload.update(
            {
                "enable_hr": True,
                "hr_scale": hr_scale,
                "hr_upscaler": hr_upscaler,
                "denoising_strength": denoising_strength or 0.5,
            }
        )

    if model:
        payload.update(
            {
                "override_settings": {"sd_model_checkpoint": model},
                "override_settings_restore_afterwards": True,
            }
        )

    response = requests.post(url=f"{address}/sdapi/v1/txt2img", json=payload, timeout=600)
    response.raise_for_status()
    data = response.json()
    if not data.get("images"):
        raise RuntimeError("Stable Diffusion returned no images")
    return base64.b64decode(data["images"][0])


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Generate NSFW images via Stable Diffusion WebUI API. Ensure your WebUI is started with --api."
        )
    )
    parser.add_argument("prompt", type=str, help="NSFW prompt text")
    parser.add_argument(
        "--address",
        type=str,
        default="http://127.0.0.1:7860",
        help="Stable Diffusion WebUI base URL",
    )
    parser.add_argument(
        "--negative",
        type=str,
        default=(
            "(lowres, worst quality, bad anatomy, extra fingers, watermark, signature)"
        ),
        help="Negative prompt",
    )
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=640)
    parser.add_argument("--steps", type=int, default=30)
    parser.add_argument("--cfg", type=float, default=7.0, help="CFG scale")
    parser.add_argument(
        "--sampler",
        type=str,
        default="DPM++ SDE Karras",
        help="Sampler name as in WebUI",
    )
    parser.add_argument("--seed", type=int, default=-1)
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Optional sd_model_checkpoint to load before generation",
    )
    parser.add_argument("--hr-scale", type=float, default=None, help="Upscale factor >1 to enable Hires.fix")
    parser.add_argument(
        "--hr-upscaler",
        type=str,
        default=None,
        help="Upscaler name (e.g. R-ESRGAN 4x+ Anime6B) when using --hr-scale",
    )
    parser.add_argument(
        "--denoise",
        type=float,
        default=0.5,
        help="Denoising strength for Hires.fix",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("output_nsfw.png"),
        help="Output image path",
    )

    args = parser.parse_args()

    try:
        image_bytes = generate_image(
            address=args.address,
            prompt=args.prompt,
            negative_prompt=args.negative,
            width=args.width,
            height=args.height,
            steps=args.steps,
            cfg_scale=args.cfg,
            sampler_name=args.sampler,
            seed=args.seed,
            model=args.model,
            hr_scale=args.hr_scale,
            hr_upscaler=args.hr_upscaler,
            denoising_strength=args.denoise,
        )
    except Exception as exc:
        print(f"Generation failed: {exc}", file=sys.stderr)
        sys.exit(1)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(image_bytes)
    print(f"Saved image -> {args.out}")


if __name__ == "__main__":
    main()

