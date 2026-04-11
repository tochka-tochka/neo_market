<script lang="ts">
    import { API_URL } from '$lib';

    let username = $state('');
    let password = $state('');
    let error = $state('');
    let loading = $state(false);

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        error = '';
        loading = true;

        try {
            const response = await fetch(`${API_URL}/login/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Ошибка входа');
            }

            const data = await response.json();
            // Сохраняем токен или перенаправляем
            window.localStorage.setItem('token', data.access);
            window.location.href = '/products';
        } catch (err) {
            error = err instanceof Error ? err.message : 'Ошибка входа';
        } finally {
            loading = false;
        }
    }
</script>

<div class="w-full max-w-md mx-auto p-6 bg-neutral-900">
    <h2 class="font-Manrope font-bold text-2xl text-white mb-6">Вход</h2>
    
    <form onsubmit={handleSubmit} class="flex flex-col gap-4">
        <div class="flex flex-col gap-2">
            <label for="login" class="font-Manrope font-light text-lg text-tx-secondary">
                Имя пользователя
            </label>
            <input
                id="username"
                type="text"
                bind:value={username}
                required
                class="border-b border-white/20 px-4 py-3 text-white text-lg font-Manrope outline-none placeholder:text-tx-secondary focus:border-white/40"
            />
        </div>

        <div class="flex flex-col gap-2">
            <label for="password" class="font-Manrope font-light text-lg text-tx-secondary">
                Пароль
            </label>
            <input
                id="password"
                type="password"
                bind:value={password}
                required
                class="border-b border-white/20 px-4 py-3 text-white text-lg font-Manrope outline-none placeholder:text-tx-secondary focus:border-white/40"
            />
        </div>

        {#if error}
            <p class="text-red-400 font-Manrope font-light text-lg">{error}</p>
        {/if}

        <button
            type="submit"
            disabled={loading}
            class="px-6 py-4 bg-white text-neutral font-Manrope font-bold text-xl cursor-pointer duration-100 hover:bg-white/90 disabled:opacity-50"
        >
            {loading ? 'Вход...' : 'Войти'}
        </button>
        <a href="/auth/register" class="text-tx-secondary text-lg font-Manrope font-semibold cursor-pointer duration-100 hover:opacity-80">Регистрация</a>
    </form>
</div>