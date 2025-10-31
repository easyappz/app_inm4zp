import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import commentsApi from '../api/comments';
import authApi from '../api/auth';
import { useQuery } from '@tanstack/react-query';

export default function CommentItem({ comment, listingId }) {
  const [isEditing, setIsEditing] = useState(false);
  const [text, setText] = useState(comment.content || '');
  const [violations, setViolations] = useState([]);
  const queryClient = useQueryClient();

  const meQuery = useQuery({ queryKey: ['authMe'], queryFn: () => authApi.me(), retry: false });

  const likeMutation = useMutation({
    mutationFn: () => commentsApi.toggleLike(comment.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', listingId] });
    },
  });

  const saveMutation = useMutation({
    mutationFn: () => commentsApi.update(comment.id, { content: text.trim() }),
    onSuccess: () => {
      setViolations([]);
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['comments', listingId] });
    },
    onError: (err) => {
      if (Array.isArray(err?.response?.data)) {
        setViolations(err.response.data);
      }
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => commentsApi.remove(comment.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comments', listingId] });
    },
  });

  const dateText = new Date(comment.created_at).toLocaleString();

  return (
    <div data-easytag="id1-react/src/components/CommentItem.jsx" className="rounded-lg border p-4 hover:bg-gray-50">
      <div data-easytag="id2-react/src/components/CommentItem.jsx" className="flex items-start justify-between gap-3">
        <div data-easytag="id3-react/src/components/CommentItem.jsx" className="min-w-0">
          <div data-easytag="id4-react/src/components/CommentItem.jsx" className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
            <span data-easytag="id5-react/src/components/CommentItem.jsx" className="font-medium text-gray-900">{comment.user?.username}</span>
            <span data-easytag="id6-react/src/components/CommentItem.jsx">{dateText}</span>
            {comment.edited ? <span data-easytag="id7-react/src/components/CommentItem.jsx" className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600">редактировано</span> : null}
          </div>
          {!isEditing ? (
            <p data-easytag="id8-react/src/components/CommentItem.jsx" className={`mt-2 text-sm ${comment.deleted ? 'text-gray-500 italic' : 'text-gray-900'}`}>{comment.content}</p>
          ) : (
            <div data-easytag="id9-react/src/components/CommentItem.jsx" className="mt-2 space-y-2">
              <textarea data-easytag="id10-react/src/components/CommentItem.jsx" value={text} onChange={(e) => setText(e.target.value)} className="h-24 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-accent focus:outline-none" />
              {violations.length > 0 ? (
                <div data-easytag="id11-react/src/components/CommentItem.jsx" className="space-y-1 rounded-md bg-red-50 p-2 text-sm text-red-700">
                  <div data-easytag="id12-react/src/components/CommentItem.jsx" className="font-medium">Обнаружены запрещённые слова:</div>
                  <ul data-easytag="id13-react/src/components/CommentItem.jsx" className="list-inside list-disc">
                    {violations.map((v) => (
                      <li data-easytag="id14-react/src/components/CommentItem.jsx" key={v.id}>{v.description}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
              <div data-easytag="id15-react/src/components/CommentItem.jsx" className="flex items-center gap-2">
                <button data-easytag="id16-react/src/components/CommentItem.jsx" onClick={() => saveMutation.mutate()} className="rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60" disabled={saveMutation.isPending}>Сохранить</button>
                <button data-easytag="id17-react/src/components/CommentItem.jsx" onClick={() => setIsEditing(false)} className="rounded-md bg-gray-100 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-200">Отмена</button>
              </div>
            </div>
          )}
        </div>
        <div data-easytag="id18-react/src/components/CommentItem.jsx" className="flex shrink-0 flex-col items-end gap-2">
          <button data-easytag="id19-react/src/components/CommentItem.jsx" onClick={() => (meQuery.data ? likeMutation.mutate() : null)} disabled={!meQuery.data} className={`rounded-md border px-2 py-1 text-sm ${meQuery.data ? 'hover:bg-gray-100' : 'opacity-60'}`}>❤️ {comment.likes_count}</button>
          {meQuery.data ? null : (
            <span data-easytag="id20-react/src/components/CommentItem.jsx" className="text-[11px] text-gray-500">Войдите, чтобы лайкать</span>
          )}
          {comment.is_owner && !comment.deleted ? (
            <div data-easytag="id21-react/src/components/CommentItem.jsx" className="flex items-center gap-2">
              {!isEditing ? (
                <button data-easytag="id22-react/src/components/CommentItem.jsx" onClick={() => setIsEditing(true)} className="rounded-md bg-gray-100 px-2 py-1 text-xs hover:bg-gray-200">Редактировать</button>
              ) : null}
              <button data-easytag="id23-react/src/components/CommentItem.jsx" onClick={() => deleteMutation.mutate()} className="rounded-md bg-red-50 px-2 py-1 text-xs text-red-700 hover:bg-red-100">Удалить</button>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
