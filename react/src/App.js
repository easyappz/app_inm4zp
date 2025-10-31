import React, { useEffect } from 'react';
import ErrorBoundary from './ErrorBoundary';
import { BrowserRouter, Routes, Route, Link, useParams } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './App.css';

const queryClient = new QueryClient();

function Layout({ children }) {
  return (
    <div data-easytag="id1-react/src/App.js" className="min-h-screen bg-background">
      <header data-easytag="id2-react/src/App.js" className="sticky top-0 z-10 bg-white shadow-card">
        <div data-easytag="id3-react/src/App.js" className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
          <div data-easytag="id4-react/src/App.js" className="flex items-center gap-2">
            <div data-easytag="id5-react/src/App.js" className="h-8 w-8 rounded-md bg-accent" aria-hidden="true" />
            <h1 data-easytag="id6-react/src/App.js" className="text-lg font-semibold text-gray-900">Easyappz · Доска</h1>
          </div>
          <nav data-easytag="id7-react/src/App.js" className="flex items-center gap-4">
            <Link data-easytag="id8-react/src/App.js" to="/" className="text-sm text-gray-700 hover:text-accent">Главная</Link>
          </nav>
        </div>
      </header>
      <main data-easytag="id9-react/src/App.js" className="mx-auto max-w-6xl px-4 py-6">
        {children}
      </main>
      <footer data-easytag="id10-react/src/App.js" className="border-t bg-white">
        <div data-easytag="id11-react/src/App.js" className="mx-auto max-w-6xl px-4 py-6 text-sm text-gray-500">© {new Date().getFullYear()} Easyappz</div>
      </footer>
    </div>
  );
}

function HomePage() {
  return (
    <section data-easytag="id12-react/src/App.js" className="grid gap-6">
      <div data-easytag="id13-react/src/App.js" className="rounded-card bg-white shadow-card p-6">
        <h2 data-easytag="id14-react/src/App.js" className="text-xl font-semibold text-gray-900">Популярные объявления</h2>
        <p data-easytag="id15-react/src/App.js" className="mt-1 text-sm text-gray-600">Здесь будет список популярных объявлений.</p>
      </div>
      <div data-easytag="id16-react/src/App.js" className="rounded-card bg-white shadow-card p-6">
        <h2 data-easytag="id17-react/src/App.js" className="text-xl font-semibold text-gray-900">Быстрый поиск по ссылке</h2>
        <p data-easytag="id18-react/src/App.js" className="mt-1 text-sm text-gray-600">Вставьте ссылку на объявление Avito, чтобы найти или создать карточку.</p>
        <div data-easytag="id19-react/src/App.js" className="mt-4 flex gap-2">
          <input data-easytag="id20-react/src/App.js" type="text" placeholder="https://www.avito.ru/..." className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-accent focus:outline-none" />
          <button data-easytag="id21-react/src/App.js" type="button" className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90">Найти</button>
        </div>
      </div>
    </section>
  );
}

function ListingPage() {
  const { id } = useParams();
  return (
    <section data-easytag="id22-react/src/App.js" className="grid gap-6">
      <div data-easytag="id23-react/src/App.js" className="rounded-card bg-white shadow-card p-6">
        <h2 data-easytag="id24-react/src/App.js" className="text-xl font-semibold text-gray-900">Объявление #{id}</h2>
        <p data-easytag="id25-react/src/App.js" className="mt-1 text-sm text-gray-600">Здесь будет информация об объявлении и комментарии.</p>
      </div>
    </section>
  );
}

function NotFoundPage() {
  return (
    <section data-easytag="id26-react/src/App.js" className="grid gap-6">
      <div data-easytag="id27-react/src/App.js" className="rounded-card bg-white shadow-card p-6">
        <h2 data-easytag="id28-react/src/App.js" className="text-xl font-semibold text-gray-900">Страница не найдена</h2>
        <p data-easytag="id29-react/src/App.js" className="mt-1 text-sm text-gray-600">Проверьте корректность адреса или вернитесь на главную.</p>
        <div data-easytag="id30-react/src/App.js" className="mt-4">
          <Link data-easytag="id31-react/src/App.js" to="/" className="inline-flex items-center rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90">На главную</Link>
        </div>
      </div>
    </section>
  );
}

function AppShell() {
  useEffect(() => {
    if (typeof window !== 'undefined' && typeof window.handleRoutes === 'function') {
      window.handleRoutes(['/', '/listing/:id', '*']);
    }
  }, []);

  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/listing/:id" element={<ListingPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppShell />
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
