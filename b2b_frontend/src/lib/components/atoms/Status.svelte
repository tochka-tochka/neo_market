<script lang="ts">
let { status }: { status: Status } = $props();

type Status = "active" | "blocked" | "on_moderation";

let statusClass: { [key in Status]: string } = {
	blocked: "text-tertiary/100",
	active: "text-secondary/100",
	on_moderation: "text-primary/100",
};

let statusTranslate: { [key in Status]: string } = {
	blocked: "Заблокирован",
	active: "В ассортименте",
	on_moderation: "На рассмотрении",
};
</script>
<p>
    <span class={`${statusClass[status]} px-3 py-2`}>{statusTranslate[status]}</span>
</p>