'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Clock, RotateCcw } from 'lucide-react';
import BottomSheet from './BottomSheet';
import { routinesAPI } from '@/lib/api';

const DAY_LABELS = ['일', '월', '화', '수', '목', '금', '토'];

interface Props {
  open: boolean;
  onClose: () => void;
  categoryId: string;
  statColor: string;
}

export default function AddRoutineSheet({ open, onClose, categoryId, statColor }: Props) {
  const qc = useQueryClient();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [frequency, setFrequency] = useState<'daily' | 'alternate' | 'weekdays'>('daily');
  const [daysOfWeek, setDaysOfWeek] = useState<number[]>([1, 3, 5]); // 기본 월수금
  const [notifTime, setNotifTime] = useState('07:00');

  const mutation = useMutation({
    mutationFn: routinesAPI.create,
    onSuccess: () => {
      // 관련 쿼리 캐시 초기화 → 자동 리페치
      qc.invalidateQueries({ queryKey: ['routines', categoryId] });
      qc.invalidateQueries({ queryKey: ['stats'] });
      qc.invalidateQueries({ queryKey: ['routines', 'today'] });
      handleClose();
    },
  });

  const handleClose = () => {
    setName(''); setDescription(''); setFrequency('daily');
    setDaysOfWeek([1, 3, 5]); setNotifTime('07:00');
    onClose();
  };

  const toggleDay = (day: number) => {
    setDaysOfWeek(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day].sort()
    );
  };

  const handleSubmit = () => {
    if (!name.trim()) return;
    mutation.mutate({
      category_id: categoryId,
      name: name.trim(),
      description: description.trim() || undefined,
      frequency,
      days_of_week: frequency === 'weekdays' ? daysOfWeek : undefined,
      notification_time: notifTime || undefined,
    });
  };

  const inputStyle = {
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.08)',
  };

  return (
    <BottomSheet open={open} onClose={handleClose} title="루틴 추가">
      <div className="space-y-4">

        {/* 루틴명 */}
        <div>
          <label className="text-xs text-gray-500 mb-1.5 block">루틴명 *</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="예: 레티놀 바르기"
            maxLength={50}
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
            placeholder="예: 취침 전 도포"
            maxLength={100}
            className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder-gray-600 outline-none"
            style={inputStyle}
          />
        </div>

        {/* 빈도 선택 */}
        <div>
          <label className="text-xs text-gray-500 mb-1.5 block">빈도</label>
          <div className="flex gap-2">
            {(['daily', 'alternate', 'weekdays'] as const).map(f => (
              <button
                key={f}
                onClick={() => setFrequency(f)}
                className="flex-1 py-2.5 rounded-xl text-xs font-semibold transition-all"
                style={{
                  background: frequency === f ? statColor + '33' : 'rgba(255,255,255,0.05)',
                  color: frequency === f ? statColor : '#6b7280',
                  border: `1px solid ${frequency === f ? statColor + '55' : 'transparent'}`,
                }}
              >
                {f === 'daily' ? '매일' : f === 'alternate' ? '격일' : '요일 선택'}
              </button>
            ))}
          </div>
        </div>

        {/* 요일 선택 (weekdays일 때만) */}
        {frequency === 'weekdays' && (
          <div>
            <label className="text-xs text-gray-500 mb-1.5 block">요일 선택</label>
            <div className="flex gap-1.5">
              {DAY_LABELS.map((label, i) => (
                <button
                  key={i}
                  onClick={() => toggleDay(i)}
                  className="flex-1 py-2 rounded-xl text-xs font-bold transition-all"
                  style={{
                    background: daysOfWeek.includes(i) ? statColor + '33' : 'rgba(255,255,255,0.05)',
                    color: daysOfWeek.includes(i) ? statColor : '#4b5563',
                    border: `1px solid ${daysOfWeek.includes(i) ? statColor + '55' : 'transparent'}`,
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* 알림 시간 */}
        <div>
          <label className="text-xs text-gray-500 mb-1.5 flex items-center gap-1">
            <Clock size={11} /> 알림 시간 (선택)
          </label>
          <input
            type="time"
            value={notifTime}
            onChange={e => setNotifTime(e.target.value)}
            className="w-full px-4 py-3 rounded-xl text-sm text-white outline-none"
            style={{ ...inputStyle, colorScheme: 'dark' }}
          />
        </div>

        {/* 에러 메시지 */}
        {mutation.isError && (
          <p className="text-xs text-red-400">추가 실패. 다시 시도해주세요.</p>
        )}

        {/* 확인 버튼 */}
        <button
          onClick={handleSubmit}
          disabled={!name.trim() || mutation.isPending}
          className="w-full py-3.5 rounded-xl text-sm font-black transition-all active:scale-[0.98] disabled:opacity-40"
          style={{ background: statColor, color: '#fff' }}
        >
          {mutation.isPending ? '추가 중...' : '루틴 추가'}
        </button>
      </div>
    </BottomSheet>
  );
}
