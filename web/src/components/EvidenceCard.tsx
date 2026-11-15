import { pictureUrl } from "../api/client";

type Props = {
  title: string;
  value: string;
  detail: string;
  source: string;
  pill: string;
  imageUrl?: string | null;
};

export function EvidenceCard({ title, value, detail, source, pill, imageUrl }: Props) {
  const picture = pictureUrl(imageUrl);
  return (
    <article className="rounded-2xl bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-full bg-lime text-sm font-extrabold text-navy">
            {title.slice(0, 1)}
          </span>
          <h2 className="font-extrabold text-navy">{title}</h2>
        </div>
        <span className="rounded-full bg-moss px-3 py-1 text-[11px] font-bold text-white">{pill}</span>
      </div>
      <p className="mt-4 text-3xl font-extrabold text-lime-dark">{value}</p>
      <p className="mt-1 text-sm leading-relaxed text-ink/65">{detail}</p>
      <p className="mt-2 text-xs font-semibold text-sky">{source}</p>
      {picture && (
        <img
          src={picture}
          alt=""
          className="mt-3 h-20 w-full rounded-lg object-cover"
          onError={(event) => {
            event.currentTarget.style.display = "none";
          }}
        />
      )}
    </article>
  );
}
