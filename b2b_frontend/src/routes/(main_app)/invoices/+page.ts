import type { PageLoad } from './$types';
import type { InvoiceType, ProductType, Char } from '$lib/types';
import { API_URL } from '$lib';

export const load: PageLoad = async ({ depends, fetch }) => {
    depends('invoices:delete', 'invoices:accept')
    try {
        const res = await fetch(`${API_URL}/invoices/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            cache: 'no-store'    
        }).then(res => res.json());
        const invoices : InvoiceType[] = res.invoices;
        return { "invoices": invoices ?? [] };
    } catch (error) {
        console.error('Error fetching invoices:', error);
        return { "invoices": [] }; 
    }
};