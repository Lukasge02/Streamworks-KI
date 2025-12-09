import { useState, useEffect } from "react";

export interface Option {
    label: string;
    value: string;
}

export function useOptions(category: string) {
    const [options, setOptions] = useState<Option[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchOptions = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/options/${category}`);
                if (res.ok) {
                    const data = await res.json();
                    setOptions(data);
                }
            } catch (error) {
                console.error(`Error loading options for ${category}:`, error);
            } finally {
                setIsLoading(false);
            }
        };

        if (category) {
            fetchOptions();
        }
    }, [category]);

    return { options, isLoading };
}
