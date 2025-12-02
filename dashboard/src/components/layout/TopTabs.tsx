import React, { useState, useRef, useEffect } from 'react';
import UserProfileWidget from './UserProfileWidget';

interface TopTabsProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck') => void;
}

const TopTabs: React.FC<TopTabsProps> = ({ currentPage, onPageChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const pages = [
    { key: 'AIS' as const, label: 'AIS' },
    { key: 'TOS' as const, label: 'TOS' },
    { key: 'TC' as const, label: 'TC' },
    { key: 'QC' as const, label: 'QC' },
    { key: 'YT' as const, label: 'YT' },
    { key: 'PortMisVsslNo' as const, label: 'PMIS→TOS' },
    { key: 'TosVsslNo' as const, label: 'TOS→PMIS' },
    { key: 'VsslSpecInfo' as const, label: '선박제원' }
  ];

  const currentPageData = pages.find(page => page.key === currentPage);

  // 외부 클릭 시 드롭다운 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handlePageChange = (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'YT' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo') => {
    onPageChange(page);
    setIsOpen(false);
  };

  return (
    <div className="relative w-full flex items-center justify-between">
      {/* 왼쪽: 페이지 네비게이션 드롭다운 */}
      <div className="relative" ref={dropdownRef}>
        {/* 드롭다운 버튼 */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-8 py-2 bg-main-bg border-none rounded-t-xl text-lg font-medium text-gray-700 hover:bg-primary hover:text-white focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all duration-200 flex items-center justify-between min-w-[200px]"
        >
          <span>{currentPageData?.label || '페이지 선택'}</span>
          <svg 
            className={`w-5 h-5 ml-2 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* 드롭다운 메뉴 */}
        {isOpen && (
          <div className="absolute top-full left-0 mt-2 bg-main-bg border border-gray-200 rounded-xl shadow-lg z-50 min-w-[200px]">
            {pages.map((page) => (
              <button
                key={page.key}
                onClick={() => handlePageChange(page.key)}
                className={`w-full px-8 py-2 text-left text-lg font-medium transition-all duration-200 first:rounded-t-xl last:rounded-b-xl ${
                  currentPage === page.key
                    ? 'bg-primary text-white'
                    : 'text-gray-700 hover:bg-primary hover:text-white'
                }`}
              >
                {page.label}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* 오른쪽: 사용자 프로필 위젯 */}
      <div className="flex-shrink-0">
        <UserProfileWidget />
      </div>
    </div>
  );
};

export default TopTabs; 