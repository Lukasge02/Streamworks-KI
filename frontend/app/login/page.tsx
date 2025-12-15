"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Lock, Mail, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, type LoginInput } from "../../lib/schemas/login";
import { Label } from "../components/ui/label";
import { Button } from "../components/ui/button";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState("");

  const form = useForm<LoginInput>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
    mode: "onBlur",
  });

  const handleLogin = async (data: LoginInput) => {
    setError("");

    try {
      // Create a real delay to simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      console.log("Logging in with", data.email);
      router.push("/testing");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "An error occurred";
      setError(message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden"
      >
        <div className="p-8">
          <div className="flex justify-center mb-6">
            <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center transform rotate-3">
              <Lock className="w-6 h-6 text-white" />
            </div>
          </div>

          <h2 className="text-2xl font-bold text-center text-slate-900 mb-2">
            Willkommen zurück
          </h2>
          <p className="text-center text-slate-500 mb-8">
            Bitte melden Sie sich an um fortzufahren
          </p>

          <form onSubmit={form.handleSubmit(handleLogin)} className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <div className="relative">
                <Mail className="absolute left-3.5 top-3 w-5 h-5 text-slate-400" />
                <input
                  id="email"
                  type="email"
                  {...form.register("email")}
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                  placeholder="name@company.com"
                />
              </div>
              {form.formState.errors.email && (
                <p className="text-red-500 text-sm mt-1">
                  {form.formState.errors.email.message}
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="password">Passwort</Label>
              <div className="relative">
                <Lock className="absolute left-3.5 top-3 w-5 h-5 text-slate-400" />
                <input
                  id="password"
                  type="password"
                  {...form.register("password")}
                  className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                  placeholder="••••••••"
                />
              </div>
              {form.formState.errors.password && (
                <p className="text-red-500 text-sm mt-1">
                  {form.formState.errors.password.message}
                </p>
              )}
            </div>

            {error && (
              <div className="p-3 bg-red-50 text-red-600 text-sm rounded-lg">
                {error}
              </div>
            )}

            <Button
              type="submit"
              isLoading={form.formState.isSubmitting}
              className="w-full bg-indigo-600 hover:bg-indigo-700"
            >
              {!form.formState.isSubmitting && (
                <>
                  Anmelden
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </Button>
          </form>
        </div>
        <div className="bg-slate-50 px-8 py-4 border-t border-slate-100 text-center text-sm text-slate-500">
          Noch keinen Account?{" "}
          <a href="#" className="text-indigo-600 font-medium hover:underline">
            Registrieren
          </a>
        </div>
      </motion.div>
    </div>
  );
}
