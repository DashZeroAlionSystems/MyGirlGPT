"use client";

import { useMemo, useState } from "react";

type Chip = { id: string; label: string; group: string };

const CHIP_GROUPS: { group: string; chips: Chip[] }[] = [
  {
    group: "Action",
    chips: [
      { id: "cafe", label: "Cafe Time", group: "Action" },
      { id: "flowers", label: "Holding Flowers", group: "Action" },
      { id: "show", label: "Show Pose", group: "Action" },
    ],
  },
  {
    group: "Outfits",
    chips: [
      { id: "dress", label: "Red Dress", group: "Outfits" },
      { id: "school", label: "School Uniform", group: "Outfits" },
      { id: "leather", label: "Leather Suit", group: "Outfits" },
    ],
  },
  {
    group: "Positions",
    chips: [
      { id: "standing", label: "Standing", group: "Positions" },
      { id: "kneeling", label: "Kneeling", group: "Positions" },
      { id: "sitting", label: "Sitting", group: "Positions" },
    ],
  },
];

type Card = { id: string; title: string; img: string };

function generateCards(count: number, offset = 0): Card[] {
  return Array.from({ length: count }).map((_, i) => {
    const id = `${offset + i}`;
    const seed = (offset + i) % 10;
    const img = `https://picsum.photos/seed/${seed}/600/800`;
    return { id, title: `Example ${offset + i + 1}`, img };
  });
}

export default function Home() {
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [page, setPage] = useState(1);

  const cards = useMemo(() => generateCards(12 * page), [page]);

  function toggleChip(id: string) {
    setSelected((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  return (
    <div className="min-h-screen w-full">
      <div className="mx-auto max-w-7xl px-4 py-6">
        <header className="mb-4 flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-pink-500" />
          <div className="text-lg font-semibold">Surprise Me!</div>
          <div className="ml-auto">
            <button className="rounded-md bg-pink-500 px-4 py-2 text-white hover:bg-pink-400">Generate</button>
          </div>
        </header>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-[300px_1fr]">
          <aside className="rounded-lg bg-neutral-800 p-4">
            <div className="mb-3 text-sm font-semibold text-neutral-200">Advanced Settings</div>
            <div className="space-y-4">
              {CHIP_GROUPS.map((group) => (
                <div key={group.group}>
                  <div className="mb-2 text-xs uppercase tracking-wide text-neutral-400">{group.group}</div>
                  <div className="flex flex-wrap gap-2">
                    {group.chips.map((chip) => {
                      const active = !!selected[chip.id];
                      return (
                        <button
                          key={chip.id}
                          onClick={() => toggleChip(chip.id)}
                          className={`rounded-md border px-3 py-1 text-sm transition-colors ${
                            active
                              ? "border-pink-400 bg-pink-500/20 text-pink-300"
                              : "border-neutral-700 bg-neutral-900 text-neutral-300 hover:bg-neutral-700"
                          }`}
                        >
                          {chip.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </aside>

          <main className="rounded-lg bg-neutral-800 p-4">
            <div className="mb-3 text-center text-sm font-semibold text-neutral-300">Examples</div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
              {cards.map((card) => (
                <div key={card.id} className="group relative overflow-hidden rounded-lg bg-neutral-900">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={card.img} alt="" className="h-48 w-full object-cover sm:h-60" />
                  <div className="absolute inset-x-0 bottom-0 flex items-center justify-between gap-2 p-2">
                    <div className="line-clamp-1 text-xs text-neutral-200">{card.title}</div>
                    <button className="rounded-md bg-neutral-200 px-2 py-1 text-[10px] font-medium text-neutral-900 transition group-hover:bg-white">Generate</button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex justify-center">
              <button
                onClick={() => setPage((p) => p + 1)}
                className="rounded-full bg-neutral-200 px-4 py-2 text-sm font-medium text-neutral-900 hover:bg-white"
              >
                Load More
              </button>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
