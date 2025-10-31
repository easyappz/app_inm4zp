import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import listingsApi from '../api/listings';
import commentsApi from '../api/comments';
import authApi from '../api/auth';
import CommentItem from '../components/CommentItem';

export default function ListingPage() {
  const { id } = useParams();
  const listingId = id;
  const queryClient = useQueryClient();
  const [newText, setNewText] = useState('');
  const [violations, setViolations] = useState([]);
  const [pagination, setPagination] = useState({ limit: 10, offset: 0 });
  const [items, setItems] = useState([]);
  const [count, setCount] = useState(0);

  const meQuery = useQuery({ queryKey: ['authMe'], queryFn: () => authApi.me(), retry: false });

  const listingQuery = useQuery({
    queryKey: ['listing', listingId],
    queryFn: () => listingsApi.getDetail(listingId),
  });

  const commentsQuery = useQuery({
    queryKey: ['comments', listingId, pagination.offset],
    queryFn: () => commentsApi.list(listingId, pagination),
    keepPreviousData: true,
  });

  useEffect(() => {
    if (commentsQuery.data) {
      const { results, count } = commentsQuery.data;
      if (pagination.offset === 0) {
        setItems(results);
      } else {
        setItems((prev) => [...prev, ...results]);
      }
      setCount(count);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [commentsQuery.data]);

  const createMutation = useMutation({
    mutationFn: () => commentsApi.create(listingId, newText.trim()),
    onSuccess: () => {
      setNewText('');
      setViolations([]);
      setPagination({ limit: pagination.limit, offset: 0 });
      queryClient.invalidateQueries({ queryKey: ['comments', listingId] });
    },
    onError: (err) => {
      const payload = err?.response?.data;
      if (Array.isArray(payload)) {
        setViolations(payload);
      }
    },
  });

  const loadMore = () => {
    const nextOffset = pagination.offset + pagination.limit;
    if (nextOffset < count) {
      setPagination((p) => ({ ...p, offset: nextOffset }));
    }
  };

  const canLoadMore = pagination.offset + pagination.limit < count;

  return (
    <div data-easytag="id1-react/src/pages/ListingPage.jsx" className="mx-auto max-w-6xl px-4 py-6">
      {listingQuery.isLoading ? (
        <div data-easytag="id2-react/src/pages/ListingPage.jsx" className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div data-easytag="id3-react/src/pages/ListingPage.jsx" className="h-64 animate-pulse rounded-lg bg-gray-200 md:col-span-1" />
          <div data-easytag="id4-react/src/pages/ListingPage.jsx" className="space-y-3 md:col-span-2">
            <div data-easytag="id5-react/src/pages/ListingPage.jsx" className="h-6 w-2/3 animate-pulse rounded bg-gray-200" />
            <div data-easytag="id6-react/src/pages/ListingPage.jsx" className="h-6 w-1/3 animate-pulse rounded bg-gray-200" />
            <div data-easytag="id7-react/src/pages/ListingPage.jsx" className="h-32 animate-pulse rounded bg-gray-200" />
          </div>
        </div>
      ) : listingQuery.isError ? (
        <div data-easytag="id8-react/src/pages/ListingPage.jsx" className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">Не удалось загрузить объявление.</div>
      ) : (
        <div data-easytag="id9-react/src/pages/ListingPage.jsx" className="grid grid-cols-1 gap-6 md:grid-cols-3">
          <div data-easytag="id10-react/src/pages/ListingPage.jsx" className="overflow-hidden rounded-lg border bg-white md:col-span-1">
            <div data-easytag="id11-react/src/pages/ListingPage.jsx" className="h-64 w-full bg-gray-100">
              {listingQuery.data?.image_url ? (
                <img data-easytag="id12-react/src/pages/ListingPage.jsx" src={listingQuery.data.image_url} alt={listingQuery.data.title} className="h-full w-full object-cover" />
              ) : (
                <div data-easytag="id13-react/src/pages/ListingPage.jsx" className="h-full w-full" />
              )}
            </div>
          </div>
          <div data-easytag="id14-react/src/pages/ListingPage.jsx" className="space-y-3 md:col-span-2">
            <h1 data-easytag="id15-react/src/pages/ListingPage.jsx" className="text-2xl font-semibold text-gray-900">{listingQuery.data?.title}</h1>
            <div data-easytag="id16-react/src/pages/ListingPage.jsx" className="text-lg font-semibold text-gray-900">{listingQuery.data?.price ? `${listingQuery.data.price} ₽` : 'Цена не указана'}</div>
            <p data-easytag="id17-react/src/pages/ListingPage.jsx" className="whitespace-pre-wrap rounded-lg border bg-white p-4 text-sm text-gray-800">{listingQuery.data?.description || 'Описание отсутствует.'}</p>
          </div>
        </div>
      )}

      <section data-easytag="id18-react/src/pages/ListingPage.jsx" className="mt-8 space-y-4">
        <h2 data-easytag="id19-react/src/pages/ListingPage.jsx" className="text-xl font-semibold text-gray-900">Комментарии</h2>

        {meQuery.data ? (
          <div data-easytag="id20-react/src/pages/ListingPage.jsx" className="rounded-lg border bg-white p-4">
            <textarea data-easytag="id21-react/src/pages/ListingPage.jsx" value={newText} onChange={(e) => setNewText(e.target.value)} placeholder="Напишите комментарий" className="h-24 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-accent focus:outline-none" />
            {violations.length > 0 ? (
              <div data-easytag="id22-react/src/pages/ListingPage.jsx" className="mt-2 space-y-1 rounded-md bg-red-50 p-2 text-sm text-red-700">
                <div data-easytag="id23-react/src/pages/ListingPage.jsx" className="font-medium">Обнаружены запрещённые слова:</div>
                <ul data-easytag="id24-react/src/pages/ListingPage.jsx" className="list-inside list-disc">
                  {violations.map((v) => (
                    <li data-easytag="id25-react/src/pages/ListingPage.jsx" key={v.id}>{v.description}</li>
                  ))}
                </ul>
              </div>
            ) : null}
            <div data-easytag="id26-react/src/pages/ListingPage.jsx" className="mt-3 flex items-center justify-end">
              <button data-easytag="id27-react/src/pages/ListingPage.jsx" onClick={() => createMutation.mutate()} disabled={!newText.trim() || createMutation.isPending} className="rounded-md bg-accent px-4 py-2 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-60">{createMutation.isPending ? 'Отправляем…' : 'Отправить'}</button>
            </div>
          </div>
        ) : (
          <div data-easytag="id28-react/src/pages/ListingPage.jsx" className="rounded-md border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">Войдите, чтобы оставлять комментарии.</div>
        )}

        {commentsQuery.isLoading && pagination.offset === 0 ? (
          <div data-easytag="id29-react/src/pages/ListingPage.jsx" className="space-y-3">
            {Array.from({ length: 3 }).map((_, i) => (
              <div data-easytag="id30-react/src/pages/ListingPage.jsx" key={i} className="h-24 animate-pulse rounded-lg bg-gray-200" />
            ))}
          </div>
        ) : commentsQuery.isError ? (
          <div data-easytag="id31-react/src/pages/ListingPage.jsx" className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">Не удалось загрузить комментарии.</div>
        ) : (
          <div data-easytag="id32-react/src/pages/ListingPage.jsx" className="space-y-3">
            {items.length === 0 ? (
              <div data-easytag="id33-react/src/pages/ListingPage.jsx" className="rounded-lg border bg-white p-4 text-sm text-gray-600">Будьте первым, кто оставит комментарий.</div>
            ) : (
              items.map((c) => <CommentItem key={c.id} comment={c} listingId={listingId} />)
            )}
            {canLoadMore ? (
              <div data-easytag="id34-react/src/pages/ListingPage.jsx" className="pt-2 text-center">
                <button data-easytag="id35-react/src/pages/ListingPage.jsx" onClick={loadMore} className="rounded-md border bg-white px-4 py-2 text-sm hover:bg-gray-50">Показать ещё</button>
              </div>
            ) : null}
          </div>
        )}
      </section>
    </div>
  );
}
