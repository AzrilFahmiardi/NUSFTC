import "./globals.css";
import "./journey.css";

export const metadata = {
  title: "茉白 MoBai - AI Flavor Intelligence Platform",
  description:
    "MoBai (茉白) - AI-assisted functional RTD beverage formulation platform. Molecular flavour compatibility, bitter-risk prediction, and off-note masking analysis.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
