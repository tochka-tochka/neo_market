import type { PageLoad } from "../$types";
import { API_URL } from "$lib";
import type { Category, ProductType } from "$lib/types";
import { currentProduct } from "$lib/stores/productStore";

export const load : PageLoad = async ({ params } : { params: { product_id: string } }) => {
    try {
        const res = await fetch(`${API_URL}/categories`, {
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        }).then(res => res.json());
        const categories = res.categories;

        return {
            "productId": params.product_id,
            "categories": structuredClone(categories) as Category[] 
        };
    } catch (error) {
        console.log(error);
    }
}