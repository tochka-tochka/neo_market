import type { PageLoad } from "../$types";
import { API_URL } from "$lib";
import type { ProductType, Char, Image } from "$lib/types";

export const load : PageLoad = async ({ params } : { params: { product_id: string } }) => {
    try {
        const res = await fetch(`${API_URL}/products/${params.product_id}/`,{
            headers: {
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        }).then(res => res.json());
        const product : ProductType = res.product;
        console.log(product)
        if (!product.skus) {
            product.skus = []
        }
        product.images = product.images.sort((a, b) => (a.order > b.order ? 1 : -1))
        return { "product" : product };
    } catch (error) {
        console.log(error);
    }
}