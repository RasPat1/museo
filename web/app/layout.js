import "./globals.css";

export const metadata = {
  title: "Museo — Discover LA Museum Exhibits",
  description:
    "Browse current and upcoming museum exhibits in Los Angeles, curate your favourites, and export them to a shareable Google Calendar.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <nav className="nav">
          <div className="container nav__inner">
            <a href="/" className="nav__logo">
              Museo
            </a>
            <ul className="nav__links">
              <li>
                <a href="/museums" className="nav__link">
                  Museums
                </a>
              </li>
              <li>
                <a href="/exhibits" className="nav__link">
                  Exhibits
                </a>
              </li>
            </ul>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
