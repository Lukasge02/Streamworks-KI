"use client";

import { FloatingInput } from "@/components/ui/floating-input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Users, User, Mail, Phone, Building2 } from "lucide-react";

/* ------------------------------------------------------------------ */
/* Props                                                               */
/* ------------------------------------------------------------------ */

interface WizardStep2Props {
  data: Record<string, any>;
  onChange: (data: Record<string, any>) => void;
}

/* ------------------------------------------------------------------ */
/* Component                                                           */
/* ------------------------------------------------------------------ */

export default function WizardStep2({ data, onChange }: WizardStep2Props) {
  function update(key: string, value: string) {
    onChange({ ...data, [key]: value });
  }

  const contactName = (data.contact_name as string) ?? "";
  const email = (data.email as string) ?? "";

  // Simple email validation
  const emailValid = !email || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Users className="h-5 w-5 text-accent" />
          Kontaktdaten
        </CardTitle>
        <CardDescription>
          Geben Sie die Kontaktinformationen des verantwortlichen Ansprechpartners ein.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-5 sm:grid-cols-2">
          {/* Contact Name */}
          <FloatingInput
            id="contact_name"
            label="Ansprechpartner"
            value={contactName}
            onChange={(v) => update("contact_name", v)}
            required
            success={contactName.length > 0}
            icon={<User className="h-4 w-4" />}
          />

          {/* Email */}
          <FloatingInput
            id="email"
            label="E-Mail"
            type="email"
            value={email}
            onChange={(v) => update("email", v)}
            required
            error={!emailValid ? "Bitte eine gueltige E-Mail-Adresse eingeben." : undefined}
            success={emailValid && email.length > 0}
            icon={<Mail className="h-4 w-4" />}
          />

          {/* Phone */}
          <FloatingInput
            id="phone"
            label="Telefon"
            type="tel"
            value={(data.phone as string) ?? ""}
            onChange={(v) => update("phone", v)}
            icon={<Phone className="h-4 w-4" />}
            helperText="Optional"
          />

          {/* Team */}
          <FloatingInput
            id="team"
            label="Team / Abteilung"
            value={(data.team as string) ?? ""}
            onChange={(v) => update("team", v)}
            icon={<Building2 className="h-4 w-4" />}
            helperText="z.B. Finanzen, IT-Operations"
          />
        </div>
      </CardContent>
    </Card>
  );
}
