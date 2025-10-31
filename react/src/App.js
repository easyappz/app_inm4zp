import React, { useEffect } from 'react';
import ErrorBoundary from './ErrorBoundary';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import './App.css';
import Header from './components/Header';
import Home from './pages/Home';
import ListingPage from './pages/ListingPage';
import NotFound from './pages/NotFound';

const queryClient = new QueryClient();

function AppShell() {
  useEffect(() => {
    if (typeof window !== 'undefined' && typeof window.handleRoutes === 'function') {
      window.handleRoutes(['/', '/listing/:id', '*']);
    }
  }, []);

  return (
    <div data-easytag="id1-react/src/App.js" className="min-h-screen bg-background">
      <Header />
      <main data-easytag="id2-react/src/App.js" className="">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/listing/:id" element={<ListingPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <footer data-easytag="id3-react/src/App.js" className="mt-10 border-t bg-white">
        <div data-easytag="id4-react/src/App.js" className="mx-auto max-w-6xl px-4 py-6 text-sm text-gray-500">© {new Date().getFullYear()} Easyappz</div>
      </footer>
    </div>
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
