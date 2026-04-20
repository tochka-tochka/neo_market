<script lang="ts">
import { goto } from "$app/navigation";

if (localStorage.getItem("token")) {
	goto("/products");
} else {
	goto("/auth/login");
}
</script>