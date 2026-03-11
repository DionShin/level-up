'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import BottomSheet from './BottomSheet';
import { categoriesAPI } from '@/lib/api';

const ICON_PRESETS = [
  '🧴','🏋️','👔','💬','🧍','🏃','😴','📚','🇺🇸','📰','📈','💳',
  '🎯','🧠','💪','🍎','🚴','🧘','✍️','🎸','📷','🌿','💊','🛁',
];

interface Props {
  open: boolean;
  onClose: () => void;
  statId: string;
  statColor: string;
}

export default function AddCategorySheet({ open, onClose, statId, statColor }: Props) {
  const qc = useQueryClient();

  const [name, setName] = useState('');
  const [icon, setIcon] = useState('🎯');
  const [description, setDescription] = useState('');

  const mutation = useMutation({
    mutationFn: categoriesAPI.create,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['categories', statId] });
      qc.invalidateQueries({ queryKey: ['stats'] });
      handleClose();
    },
  });

  const handleClose = () => {
    setName(''); setIcon('🎯'); setDescription('');
    onClose();
  };

  const handleSubmit = () => {
    if (!name.trim()) return;
    mutation.mutate({
      stat_id: statId,
      name: name.trim(),
      icon,
      description: description.trim() || undefined,
    });
  };

  const inputStyle = {
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.08)',
  };

  return (
    <BottomSheet open={open} onClose={handleClose} title="카테고리 추가">
      <div className="space-y-4">

        {/* 아이콘 선택 */}
        <div>
          <label className="text-xs text-gray-500 mb-2 block">아이콘 선택</label>
          {/* 선택된 아이콘 미리보기 */}
          <div className="flex items-center gap-3 mb-3">
            <div
              className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl"
              style={{ background: statColor + '20' }}
            >
              {icon}
            </div>
            <span className="text-xs text-gray-500">선택된 아이콘</span>
          </div>
          {/* 프리셋 그리드 */}
          <div className="grid grid-cols-8 gap-1.5">
            {ICON_PRESETS.map(e => (
              <button
                key={e}
                onClick={() => setIcon(e)}
                className="aspect-square rounded-xl text-xl flex items-center justify-center transition-all"
                style={{
                  background: icon === e ? statColor + '33' : 'rgba(255,255,255,0.05)',
                  border: `1px solid ${icon === e ? statColor + '66' : 'transparent'}`,
                }}
              >
                {e}
              </button>
            ))}
          </div>
        </div>

        {/* 카테고리명 */}
        <div>
          <label className="text-xs text-gray-500 mb-1.5 block">카테고리명 *</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="예: 피부관리"
            maxLength={30}
            className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder-gray-600 outline-none"
            style={inputStyle}
          />
        </div>

        {/* 설명 */}
        <div>
          <label className="text-xs text-gray-500 mb-1.5 block">설명 (선택)</label>
          <input
            type="text"
            value={description}
            onChange={e => setDescription(e.target.value)}
            placeholder="예: 매일 스킨케어 루틴 관리"
            maxLength={80}
            className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder-gray-600 outline-none"
            style={inputStyle}
          />
        </div>

        {mutation.isError && (
          <p className="text-xs text-red-400">추가 실패. 다시 시도해주세요.</p>
        )}

        <button
          onClick={handleSubmit}
          disabled={!name.trim() || mutation.isPending}
          className="w-full py-3.5 rounded-xl text-sm font-black transition-all active:scale-[0.98] disabled:opacity-40"
          style={{ background: statColor, color: '#fff' }}
        >
          {mutation.isPending ? '추가 중...' : '카테고리 추가'}
        </button>
      </div>
    </BottomSheet>
  );
}
