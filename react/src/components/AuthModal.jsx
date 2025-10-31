import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { auth } from '../api/auth';

export default function AuthModal({ open, onClose }) {
  const [tab, setTab] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errorText, setErrorText] = useState('');
  const queryClient = useQueryClient();

  const onSuccessAuth = (data) => {
    try {
      if (data?.token) {
        localStorage.setItem('token', data.token);
      }
      queryClient.invalidateQueries({ queryKey: ['authMe'] });
      if (typeof onClose === 'function') onClose();
    } catch (e) {
      // no-op
    }
  };

  const loginMutation = useMutation({
    mutationFn: ({ username, password }) => auth.login({ username, password }),
    onSuccess: onSuccessAuth,
    onError: (err) => {
      const m = err?.response?.data;
      setErrorText(typeof m === 'string' ? m : 'Не удалось войти. Проверьте данные.');
    },
  });

  const registerMutation = useMutation({
    mutationFn: ({ username, password }) => auth.register({ username, password }),
    onSuccess: onSuccessAuth,
    onError: (err) => {
      const m = err?.response?.data;
      setErrorText(typeof m === 'string' ? m : 'Не удалось зарегистрироваться.');
    },
  });

  const submit = (e) => {
    e.preventDefault();
    setErrorText('');
    const payload = { username: username.trim(), password };
    if (tab === 'login') {
      loginMutation.mutate(payload);
    } else {
      registerMutation.mutate(payload);
    }
  };

  if (!open) return null;

  return (
    <div data-easytag="id1-react/src/components/AuthModal.jsx" className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div data-easytag="id2-react/src/components/AuthModal.jsx" className="w-full max-w-md rounded-lg bg-white shadow-xl">
        <div data-easytag="id3-react/src/components/AuthModal.jsx" className="flex items-center justify-between border-b px-5 py-4">
          <h3 data-easytag="id4-react/src/components/AuthModal.jsx" className="text-lg font-semibold">Авторизация</h3>
          <button data-easytag="id5-react/src/components/AuthModal.jsx" onClick={onClose} className="rounded p-1 text-gray-500 hover:bg-gray-100">✕</button>
        </div>
        <div data-easytag="id6-react/src/components/AuthModal.jsx" className="px-5 pt-4">
          <div data-easytag="id7-react/src/components/AuthModal.jsx" className="mb-4 grid grid-cols-2 gap-2">
            <button data-easytag="id8-react/src/components/AuthModal.jsx" onClick={() => setTab('login')} className={`rounded-md px-3 py-2 text-sm font-medium ${tab === 'login' ? 'bg-accent text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>Вход</button>
            <button data-easytag="id9-react/src/components/AuthModal.jsx" onClick={() => setTab('register')} className={`rounded-md px-3 py-2 text-sm font-medium ${tab === 'register' ? 'bg-accent text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}>Регистрация</button>
          </div>
          <form data-easytag="id10-react/src/components/AuthModal.jsx" onSubmit={submit} className="space-y-3">
            <div data-easytag="id11-react/src/components/AuthModal.jsx" className="space-y-1">
              <label data-easytag="id12-react/src/components/AuthModal.jsx" className="block text-sm text-gray-700">Логин</label>
              <input data-easytag="id13-react/src/components/AuthModal.jsx" value={username} onChange={(e) => setUsername(e.target.value)} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-accent focus:outline-none" placeholder="Введите логин" />
            </div>
            <div data-easytag="id14-react/src/components/AuthModal.jsx" className="space-y-1">
              <label data-easytag="id15-react/src/components/AuthModal.jsx" className="block text-sm text-gray-700">Пароль</label>
              <input data-easytag="id16-react/src/components/AuthModal.jsx" type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-accent focus:outline-none" placeholder="Введите пароль" />
            </div>

            {errorText ? (
              <div data-easytag="id17-react/src/components/AuthModal.jsx" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{errorText}</div>
            ) : null}

            <button data-easytag="id18-react/src/components/AuthModal.jsx" type="submit" disabled={loginMutation.isPending || registerMutation.isPending} className="w-full rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-60">
              {tab === 'login' ? (loginMutation.isPending ? 'Входим…' : 'Войти') : (registerMutation.isPending ? 'Создаём…' : 'Зарегистрироваться')}
            </button>
          </form>
          <div data-easytag="id19-react/src/components/AuthModal.jsx" className="h-4" />
        </div>
      </div>
    </div>
  );
}
