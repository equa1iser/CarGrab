"use client";

import { useState, useCallback } from "react";
import useEmblaCarousel from "embla-carousel-react";
import Image from "next/image";
import { ChevronLeft, ChevronRight, X, ZoomIn } from "lucide-react";
import { Photo } from "@/types";

interface Props {
  photos: Photo[];
  title?: string | null;
}

export function PhotoGallery({ photos, title }: Props) {
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);
  const [emblaRef, emblaApi] = useEmblaCarousel({ loop: true });

  const scrollPrev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);

  if (photos.length === 0) {
    return (
      <div className="aspect-video glass rounded-xl flex items-center justify-center text-slate-600">
        <span className="text-sm">No photos available</span>
      </div>
    );
  }

  return (
    <>
      {/* Main carousel */}
      <div className="relative group rounded-xl overflow-hidden">
        <div className="overflow-hidden" ref={emblaRef}>
          <div className="flex">
            {photos.map((photo, i) => (
              <div key={photo.id} className="relative flex-none w-full aspect-video bg-navy-800">
                <Image
                  src={photo.url}
                  alt={`${title ?? "Vehicle"} photo ${i + 1}`}
                  fill
                  className="object-cover cursor-zoom-in"
                  sizes="(max-width: 768px) 100vw, 70vw"
                  unoptimized
                  onClick={() => setLightboxIndex(i)}
                />
              </div>
            ))}
          </div>
        </div>

        {/* Nav arrows */}
        {photos.length > 1 && (
          <>
            <button
              onClick={scrollPrev}
              className="absolute left-3 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity glass rounded-full p-2"
            >
              <ChevronLeft className="h-4 w-4 text-white" />
            </button>
            <button
              onClick={scrollNext}
              className="absolute right-3 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity glass rounded-full p-2"
            >
              <ChevronRight className="h-4 w-4 text-white" />
            </button>
          </>
        )}

        {/* Photo count */}
        <div className="absolute bottom-3 right-3 glass rounded-full px-2.5 py-1 text-xs text-slate-300">
          {photos.length} photos
        </div>
      </div>

      {/* Thumbnail strip */}
      {photos.length > 1 && (
        <div className="flex gap-2 mt-3 overflow-x-auto pb-1">
          {photos.slice(0, 8).map((photo, i) => (
            <button
              key={photo.id}
              onClick={() => { emblaApi?.scrollTo(i); }}
              className="relative flex-none w-16 h-12 rounded-lg overflow-hidden border border-white/10 hover:border-cyan-400/40 transition-colors"
            >
              <Image src={photo.url} alt="" fill className="object-cover" sizes="64px" unoptimized />
            </button>
          ))}
        </div>
      )}

      {/* Lightbox */}
      {lightboxIndex !== null && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setLightboxIndex(null)}
        >
          <button className="absolute top-4 right-4 text-white/70 hover:text-white">
            <X className="h-6 w-6" />
          </button>
          <div className="relative max-w-5xl w-full aspect-video" onClick={(e) => e.stopPropagation()}>
            <Image
              src={photos[lightboxIndex].url}
              alt=""
              fill
              className="object-contain"
              sizes="100vw"
              unoptimized
            />
          </div>
        </div>
      )}
    </>
  );
}
