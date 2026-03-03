import Link from "next/link";

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="hero__content">
          <h1 className="hero__title">
            Discover LA&rsquo;s Best <span>Museum Exhibits</span>
          </h1>
          <p className="hero__subtitle">
            Browse current and upcoming exhibits across Los Angeles&rsquo;s top
            museums. Pick the ones you love, skip the rest, and export your
            shortlist to a shareable Google Calendar.
          </p>
          <div className="hero__actions">
            <Link href="/museums" className="btn btn--primary">
              Choose Museums
            </Link>
            <Link href="/exhibits" className="btn btn--secondary">
              Browse Exhibits
            </Link>
          </div>
        </div>
      </section>

      <div className="container">
        <div className="stats">
          <div className="stat">
            <div className="stat__value">6</div>
            <div className="stat__label">Museums</div>
          </div>
          <div className="stat">
            <div className="stat__value">76</div>
            <div className="stat__label">Exhibits</div>
          </div>
          <div className="stat">
            <div className="stat__value">1</div>
            <div className="stat__label">Click to Calendar</div>
          </div>
        </div>
      </div>
    </>
  );
}
