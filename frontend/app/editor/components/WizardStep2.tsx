"use client";

import { useState, useEffect, useCallback, useImperativeHandle, forwardRef } from "react";
import { motion } from "framer-motion";
import {
  User,
  Mail,
  Phone,
  Building2,
  Users,
  Sparkles,
} from "lucide-react";

interface WizardSession {
  session_id: string;
  params: Record<string, string | boolean | number>;
  ai_suggestions?: Record<string, string>;
}

interface Props {
  session: WizardSession | null;
  onSave: (
    stepId: string,
    data: Record<string, unknown>,
    shouldAdvance?: boolean,
  ) => Promise<void>;
  isLoading: boolean;
}

export interface WizardStepRef {
  getFormData: () => Record<string, unknown>;
}

const WizardStep2Contact = forwardRef<WizardStepRef, Props>(({
  session,
  onSave,
  isLoading,
}, ref) => {
  // Form state - expanded with all contact fields
  const [contactName, setContactName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [team, setTeam] = useState("");
  const [company, setCompany] = useState("");

  // Track AI suggestions
  const [hasAiSuggestions, setHasAiSuggestions] = useState(false);

  // Load from session params
  useEffect(() => {
    if (session?.params) {
      // Handle both formats: contact_name or contact_first_name + contact_last_name
      const existingName = session.params.contact_name as string ||
        [session.params.contact_first_name, session.params.contact_last_name]
          .filter(Boolean).join(" ");
      if (existingName) setContactName(existingName);

      if (session.params.contact_email) setEmail(session.params.contact_email as string);
      if (session.params.contact_phone) setPhone(session.params.contact_phone as string);
      if (session.params.team) setTeam(session.params.team as string);
      if (session.params.department) setTeam(session.params.department as string);
      if (session.params.company_name) setCompany(session.params.company_name as string);

      // Check if we have AI suggestions
      setHasAiSuggestions(
        !!(session.ai_suggestions?.contact_name ||
          session.ai_suggestions?.contact_email ||
          session.params.contact_name ||
          session.params.contact_email)
      );
    }
  }, [session?.params, session?.ai_suggestions]);

  // Expose getFormData for parent save-on-navigate
  const getFormData = useCallback(() => ({
    contact_name: contactName,
    contact_email: email,
    contact_phone: phone,
    team: team,
    company_name: company,
  }), [contactName, email, phone, team, company]);

  useImperativeHandle(ref, () => ({
    getFormData
  }), [getFormData]);

  // Auto-save on changes (debounced)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (contactName || email) {
        onSave("contact", getFormData(), false);
      }
    }, 1500);
    return () => clearTimeout(timer);
  }, [contactName, email, phone, team, company, onSave, getFormData]);

  const inputBaseClass = `
    w-full px-4 py-3 rounded-xl border-2 transition-all duration-200
    bg-white text-gray-900 placeholder:text-gray-400
    focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-[#0082D9]
    hover:border-gray-300
  `;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="relative">
        <div className="absolute -top-2 -left-2 w-16 h-16 bg-gradient-to-br from-purple-500/20 to-pink-500/10 rounded-full blur-2xl" />
        <div className="relative">
          <h2 className="text-2xl font-bold text-gray-900 mb-2 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
              <User className="w-5 h-5 text-white" />
            </div>
            Ansprechpartner
          </h2>
          <p className="text-gray-500">
            Wer ist verantwortlich für diesen Stream?
          </p>
        </div>
      </div>

      {/* AI Suggestion Banner */}
      {hasAiSuggestions && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-100"
        >
          <div className="p-1.5 bg-purple-100 rounded-lg">
            <Sparkles className="w-4 h-4 text-purple-600" />
          </div>
          <span className="text-sm text-purple-700">
            Kontaktdaten wurden aus Ihrer Beschreibung vorausgefüllt
          </span>
        </motion.div>
      )}

      {/* Form Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Contact Name */}
        <div className="md:col-span-2">
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <User className="w-4 h-4 text-gray-400" />
            Name des Ansprechpartners
            <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={contactName}
            onChange={(e) => setContactName(e.target.value)}
            placeholder="Max Mustermann"
            className={`${inputBaseClass} ${contactName ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'}`}
          />
        </div>

        {/* Email */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Mail className="w-4 h-4 text-gray-400" />
            E-Mail Adresse
            <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="max.mustermann@firma.de"
            className={`${inputBaseClass} ${email ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'}`}
          />
        </div>

        {/* Phone */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Phone className="w-4 h-4 text-gray-400" />
            Telefonnummer
          </label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="+49 123 456789"
            className={`${inputBaseClass} ${phone ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'}`}
          />
        </div>

        {/* Team/Department */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Users className="w-4 h-4 text-gray-400" />
            Team / Abteilung
          </label>
          <input
            type="text"
            value={team}
            onChange={(e) => setTeam(e.target.value)}
            placeholder="IT Operations"
            className={`${inputBaseClass} ${team ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'}`}
          />
        </div>

        {/* Company */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
            <Building2 className="w-4 h-4 text-gray-400" />
            Unternehmen
          </label>
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            placeholder="Ihre Firma GmbH"
            className={`${inputBaseClass} ${company ? 'border-emerald-300 bg-emerald-50/30' : 'border-gray-200'}`}
          />
        </div>
      </div>

      {/* Validation Status */}
      {(contactName && email) && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-2 px-4 py-3 bg-emerald-50 rounded-xl border border-emerald-200"
        >
          <div className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="text-sm text-emerald-700">Pflichtfelder ausgefüllt</span>
        </motion.div>
      )}
    </div>
  );
});

WizardStep2Contact.displayName = "WizardStep2Contact";

export default WizardStep2Contact;
