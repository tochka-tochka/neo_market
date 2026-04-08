import type { PageLoad } from "../$types";
import { API_URL } from "$lib";

export const load : PageLoad = async ({ params }) => {
    try {
        const res = await fetch(`${API_URL}/products/${params.product_id}`);
        const product = await res.json();
        return { "product": product };
    } catch (error) {
        console.log(error);
    }
};