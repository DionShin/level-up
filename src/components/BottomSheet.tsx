'use client';

import { useEffect } from 'react';
import { X } from 'lucide-react';

interface Props {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

/**
 * 하단에서 슬라이드업되는 모달 시트.
 * 파이썬의 컨텍스트 매니저처럼 open/onClose로 생명주기 관리.
 */
export default function BottomSheet({ open, onClose, title, children }: Props) {
  // 열려있을 때 body 스크롤 잠금
  useEffect(() => {
    if (open) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = '';
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center">
      {/* 딤 배경 */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* 시트 본체 */}
      <div
        className="relative w-full max-w-[480px] rounded-t-[2rem] px-5 pt-5 pb-8"
        style={{ background: '#0f1117', border: '1px solid rgba(255,255,255,0.07)' }}
      >
        {/* 핸들 바 */}
        <div className="w-10 h-1 rounded-full bg-white/20 mx-auto mb-5" />

        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-base font-black text-white">{title}</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl"
            style={{ background: 'rgba(255,255,255,0.06)' }}
          >
            <X size={16} className="text-gray-400" />
          </button>
        </div>

        {children}
      </div>
    </div>
  );
}
