import type { ReactNode } from "react";
import { CandidateShell } from "../components/candidate-shell";
import "./globals.css";

export const metadata = {
  title: "FinBridge Cloud — uCloudify Candidate Demo",
  description: "Independent synthetic finance-data modernization candidate demonstration.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body><CandidateShell>{children}</CandidateShell></body>
    </html>
  );
}
