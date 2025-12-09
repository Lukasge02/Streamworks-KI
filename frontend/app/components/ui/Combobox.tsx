"use client";

import { useState, useRef, useEffect } from "react";
import { ChevronDown, Check } from "lucide-react";
import { cn } from "@/app/utils/cn";

interface ComboboxOption {
    value: string;
    label: string;
}

interface ComboboxProps {
    value: string;
    onChange: (value: string) => void;
    options: ComboboxOption[];
    placeholder?: string;
    className?: string;
}

export function Combobox({ value, onChange, options, placeholder = "Auswählen...", className }: ComboboxProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [search, setSearch] = useState(value);
    const containerRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Filter options based on search
    const filteredOptions = options.filter(opt =>
        opt.label.toLowerCase().includes(search.toLowerCase())
    );

    // Close dropdown on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setIsOpen(false);
                // Reset search to current value if closed without selection
                setSearch(value);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, [value]);

    // Sync search with value
    useEffect(() => {
        setSearch(value);
    }, [value]);

    const handleSelect = (opt: ComboboxOption) => {
        onChange(opt.label);
        setSearch(opt.label);
        setIsOpen(false);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(e.target.value);
        onChange(e.target.value);
        if (!isOpen) setIsOpen(true);
    };

    return (
        <div ref={containerRef} className={cn("relative", className)}>
            <div className="relative">
                <input
                    ref={inputRef}
                    type="text"
                    value={search}
                    onChange={handleInputChange}
                    onFocus={() => setIsOpen(true)}
                    placeholder={placeholder}
                    className={cn(
                        "w-full px-4 py-3 pr-10 rounded-xl border transition-all duration-200",
                        "focus:outline-none focus:ring-2 focus:ring-[#0082D9]/20 focus:border-[#0082D9]",
                        "placeholder:text-gray-400 border-gray-200 bg-white hover:border-gray-300"
                    )}
                />
                <button
                    type="button"
                    onClick={() => setIsOpen(!isOpen)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
                >
                    <ChevronDown className={cn(
                        "w-5 h-5 transition-transform duration-200",
                        isOpen && "rotate-180"
                    )} />
                </button>
            </div>

            {/* Dropdown */}
            {isOpen && (
                <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden animate-in fade-in-0 zoom-in-95 duration-100">
                    {filteredOptions.length === 0 ? (
                        <div className="px-4 py-3 text-sm text-gray-500 text-center">
                            Keine Optionen gefunden
                        </div>
                    ) : (
                        <div className="max-h-60 overflow-y-auto py-1">
                            {filteredOptions.map((opt) => {
                                const isSelected = opt.label === value;
                                return (
                                    <button
                                        key={opt.value}
                                        type="button"
                                        onClick={() => handleSelect(opt)}
                                        className={cn(
                                            "w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors",
                                            isSelected
                                                ? "bg-[#0082D9]/10 text-[#0082D9]"
                                                : "hover:bg-gray-50 text-gray-700"
                                        )}
                                    >
                                        <div className="flex-1">
                                            <span className="font-medium">{opt.label}</span>
                                        </div>
                                        {isSelected && (
                                            <Check className="w-4 h-4 text-[#0082D9] flex-shrink-0" />
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
