<script lang="ts">
    import { API_URL } from '$lib';

    let username = $state('');
    let password = $state('');
    let confirmPassword = $state('');
    let error = $state('');
    let loading = $state(false);

    async function handleSubmit(e: SubmitEvent) {
        e.preventDefault();
        error = '';

        if (password !== confirmPassword) {
            error = 'Пароли не совпадают';
            return;
        }

        loading = true;

        try {
            const response = await fetch(`${API_URL}/reg/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || 'Ошибка регистрации');
            }

            window.localStorage.setItem('token', data.access)

            // Перенаправляем на страницу входа
            window.location.href = '/my_products';
        } catch (err) {
            error = err instanceof Error ? err.message : 'Ошибка регистрации';
        } finally {
            loading = false;
        }
    }
</script>

<div class="w-full max-w-md mx-auto p-6 bg-neutral-900">
    <h2 class="font-Manrope font-bold text-2xl text-white mb-6">Регистрация</h2>
    
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
                minlength="6"
                class="border-b border-white/20 px-4 py-3 text-white text-lg font-Manrope outline-none placeholder:text-tx-secondary focus:border-white/40"
            />
        </div>

        <div class="flex flex-col gap-2">
            <label for="confirmPassword" class="font-Manrope font-light text-lg text-tx-secondary">
                Подтверждение пароля
            </label>
            <input
                id="confirmPassword"
                type="password"
                bind:value={confirmPassword}
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
            class="px-6 py-4 bg-white text-neutral font-Manrope font-bold text-xl hover:bg-white/90 disabled:opacity-50"
        >
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </button>
        <a href="/auth/login" class="text-tx-secondary text-lg font-Manrope font-semibold cursor-pointer duration-100 hover:opacity-80">Вход</a>
    </form>
</div>