// Force dynamic rendering for this route segment
// This prevents build-time pre-rendering which fails with useSearchParams
export const dynamic = "force-dynamic";

export default function WizardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
