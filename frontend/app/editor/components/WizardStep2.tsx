"use client";

import { useState, useEffect } from "react";
import { FormField, InputField } from "../../components/ui/FormField";

interface WizardSession {
    session_id: string;
    params: Record<string, string | boolean | number>;
}

interface Props {
    session: WizardSession | null;
    onSave: (stepId: string, data: Record<string, unknown>, shouldAdvance?: boolean) => Promise<void>;
    isLoading: boolean;
}

export default function WizardStep2Contact({ session, onSave, isLoading }: Props) {
    const [firstName, setFirstName] = useState(session?.params.contact_first_name as string || "");
    const [lastName, setLastName] = useState(session?.params.contact_last_name as string || "");
    const [company, setCompany] = useState(session?.params.company_name as string || "");
    const [department, setDepartment] = useState(session?.params.department as string || "");

    useEffect(() => {
        if (session?.params.contact_first_name) setFirstName(session.params.contact_first_name as string);
        if (session?.params.contact_last_name) setLastName(session.params.contact_last_name as string);
        if (session?.params.company_name) setCompany(session.params.company_name as string);
        if (session?.params.department) setDepartment(session.params.department as string);
    }, [session?.params]);

    // Auto-save effect
    useEffect(() => {
        const timer = setTimeout(() => {
            const hasChanges =
                firstName !== session?.params.contact_first_name ||
                lastName !== session?.params.contact_last_name ||
                company !== session?.params.company_name ||
                department !== session?.params.department;

            if (hasChanges && (firstName || lastName)) {
                onSave("contact", {
                    contact_first_name: firstName,
                    contact_last_name: lastName,
                    company_name: company,
                    department: department,
                }, false);
            }
        }, 1000);
        return () => clearTimeout(timer);
    }, [firstName, lastName, company, department, onSave, session?.params]);

    const handleContinue = async () => {
        await onSave("contact", {
            contact_first_name: firstName,
            contact_last_name: lastName,
            company_name: company,
            department: department,
        });
    };

    const isValid = firstName.trim() && lastName.trim();

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-bold text-gray-900 mb-1">
                    Schritt 2: Ansprechperson
                </h2>
                <p className="text-gray-500 text-sm">
                    Wer ist verantwortlich für diesen Stream?
                </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <FormField
                    label="Vorname"
                    hint="Der Vorname der verantwortlichen Ansprechperson für diesen Stream."
                    required
                >
                    <InputField
                        type="text"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        placeholder="Max"
                    />
                </FormField>

                <FormField
                    label="Nachname"
                    hint="Der Nachname der verantwortlichen Ansprechperson."
                    required
                >
                    <InputField
                        type="text"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        placeholder="Mustermann"
                    />
                </FormField>

                <FormField
                    label="Firma"
                    hint="Optional: Der Name Ihrer Firma oder Organisation."
                >
                    <InputField
                        type="text"
                        value={company}
                        onChange={(e) => setCompany(e.target.value)}
                        placeholder="Ihre Firma GmbH"
                    />
                </FormField>

                <FormField
                    label="Abteilung"
                    hint="Optional: Die Abteilung, die den Stream betreibt."
                >
                    <InputField
                        type="text"
                        value={department}
                        onChange={(e) => setDepartment(e.target.value)}
                        placeholder="IT Operations"
                    />
                </FormField>
            </div>
        </div>
    );
}
