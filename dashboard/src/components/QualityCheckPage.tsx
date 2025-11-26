import React, { useState, useEffect } from 'react';
import { DATA_TYPES, DATA_TYPES_BY_CATEGORY, DataTypeConfig, APIParams, QualityCheckRule } from '../data/qualityCheckConfig';
import { runQualityCheck, getQualityCheckHistory, QualityCheckResult, QualityCheckHistory } from '../services/qualityCheckService';
import Sidebar from './layout/Sidebar';
import TopTabs from './layout/TopTabs';
import '../styles/DashboardLayout.css';

interface QualityCheckPageProps {
  currentPage: 'AIS' | 'TOS' | 'TC' | 'QC' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck';
  onPageChange: (page: 'AIS' | 'TOS' | 'TC' | 'QC' | 'PortMisVsslNo' | 'TosVsslNo' | 'VsslSpecInfo' | 'QualityCheck') => void;
}

const QualityCheckPage: React.FC<QualityCheckPageProps> = ({ currentPage, onPageChange }) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedDataType, setSelectedDataType] = useState<DataTypeConfig | null>(null);
  const [apiParams, setApiParams] = useState<APIParams>({});
  const [qualityMeta, setQualityMeta] = useState<QualityCheckRule>({});
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<QualityCheckResult | null>(null);
  const [history, setHistory] = useState<QualityCheckHistory[]>([]);
  const [activeTab, setActiveTab] = useState<'config' | 'results' | 'history'>('config');
  const [qualityRuleTab, setQualityRuleTab] = useState<'DV' | 'DC' | 'DU' | 'DT' | 'DI'>('DV');

  // 데이터 타입별 설명 데이터
  const getApiParameterDescription = (dataType: DataTypeConfig | null) => {
    if (!dataType) return null;
    
    switch (dataType.id) {
      case 'tc_work_info':
        return {
          title: 'TC 작업정보 API 파라미터',
          parameters: [
            { code: 'tmnlId*', name: '터미널 ID', required: true, type: 'String', example: '"BPTS"' },
            { code: 'shpCd*', name: '선박코드', required: true, type: 'String', example: '"HASM"' },
            { code: 'callYr*', name: '호출연도', required: true, type: 'String', example: '"2021"' },
            { code: 'serNo*', name: '입항횟수', required: true, type: 'String', example: '"012"' },
            { code: 'timeFrom', name: '작업일시 From', required: false, type: 'Date', format: 'YYYYMMDDHHmmss', example: '"20220110000000"' },
            { code: 'timeTo', name: '작업일시 To', required: false, type: 'Date', format: 'YYYYMMDDHHmmss', example: '"20220130235959"' }
          ],
          note: 'timeFrom 또는 timeTo 중 최소 하나는 필수입니다.'
        };
      case 'qc_work_info':
        return {
          title: 'QC 작업정보 API 파라미터',
          parameters: [
            { code: 'tmnlId*', name: '터미널 ID', required: true, type: 'String', example: '"BPTS"' },
            { code: 'shpCd*', name: '선박코드', required: true, type: 'String', example: '"HASM"' },
            { code: 'callYr*', name: '호출연도', required: true, type: 'String', example: '"2021"' },
            { code: 'serNo*', name: '입항횟수', required: true, type: 'String', example: '"012"' }
          ],
          note: null
        };
      default:
        return {
          title: 'API 파라미터',
          parameters: [],
          note: null
        };
    }
  };

  const getQualityRuleDescription = (dataType: DataTypeConfig | null) => {
    if (!dataType) return null;
    
    switch (dataType.id) {
      case 'tc_work_info':
        return {
          title: 'TC 작업정보 품질 검사 규칙',
          rules: [
            {
              code: 'DV',
              name: '유효성 검사',
              subRules: [
                { 
                  name: 'RANGE', 
                  description: '값 범위 검사', 
                  details: [
                    'serNo: 0~999 사이의 정수값이어야 함',
                    'callYr: 2000~2100 사이의 연도값이어야 함',
                    '',
                    'RANGE 규칙 파라미터 설명',
                    'rtype: 데이터 타입 (I=정수형, F=실수형)',
                    'ctype: 검사 방식 (I=범위내, O=범위외)',
                    'val1: 최소값 또는 범위 시작값',
                    'val2: 최대값 또는 범위 종료값',
                    '',
                    '예시: {"rtype": "I", "ctype": "I", "val1": 2000, "val2": 2100}',
                    'callYr은 정수형이며 2000~2100 사이의 값이어야 함'
                  ] 
                },
                { 
                  name: 'DATE', 
                  description: '날짜 형식 및 유효성 검사', 
                  details: [
                    'wkTime: 1900년 1월 1일 이후의 유효한 날짜여야 함',
                    '',
                    'DATE 규칙 파라미터 설명',
                    '날짜 형식: YYYY-MM-DD 또는 YYYYMMDD',
                    '기준 날짜: 1900-01-01 이후의 유효한 날짜',
                    '시간 포함: YYYYMMDDHHmmss 형식도 지원'
                  ] 
                }
              ]
            },
            {
              code: 'DC',
              name: '일관성 검사',
              subRules: [
                { 
                  name: 'DUPLICATE', 
                  description: '중복값 검사', 
                  details: [
                    'tmnlId: 터미널 ID는 고유해야 함 (중복 불가)',
                    'serNo: 입항횟수는 고유해야 함 (중복 불가)',
                    '',
                    'DUPLICATE 규칙 파라미터 설명',
                    '고유성 검사: 동일한 값이 중복되어 있으면 안됨',
                    '복합 키: 여러 필드를 조합한 고유성도 검사 가능',
                    'NULL 값: NULL 값은 중복 검사에서 제외'
                  ] 
                }
              ]
            },
            {
              code: 'DU',
              name: '사용성 검사',
              subRules: [
                { 
                  name: 'USAGE', 
                  description: '필드 사용성 검사', 
                  details: [
                    'tmnlId(터미널 ID): 터미널 ID 필드가 실제로 사용되고 있는지 확인',
                    'wkTime(작업일시): 작업일시 필드가 실제로 사용되고 있는지 확인',
                    'serNo(입항횟수): 입항횟수 필드가 실제로 사용되고 있는지 확인',
                    'callYr(호출연도): 호출연도 필드가 실제로 사용되고 있는지 확인',
                    '',
                    'USAGE 규칙 파라미터 설명',
                    '사용률 검사: 필드가 실제로 사용되는 비율을 확인',
                    '임계값 설정: 사용률이 일정 수준 이상이어야 함',
                    '의미있는 데이터: NULL이 아닌 유효한 값의 사용률을 측정'
                  ] 
                }
              ]
            }
          ]
        };
      case 'qc_work_info':
        return {
          title: 'QC 작업정보 품질 검사 규칙',
          rules: [
            {
              code: 'DV',
              name: '유효성 검사',
              subRules: [
                { name: 'RANGE', description: '값 범위 검사', details: ['serNo: 0~999 사이의 정수값이어야 함', 'callYr: 2000~2100 사이의 연도값이어야 함'] }
              ]
            }
          ]
        };
      default:
        return {
          title: '품질 검사 규칙',
          rules: []
        };
    }
  };

  // 데이터 타입 선택 시 기본값 설정
  useEffect(() => {
    if (selectedDataType) {
      setApiParams(selectedDataType.defaultParams);
      setQualityMeta(selectedDataType.defaultMeta);
    }
  }, [selectedDataType]);

  // 히스토리 로드
  useEffect(() => {
    const loadHistory = async () => {
      try {
        const historyData = await getQualityCheckHistory();
        setHistory(historyData);
      } catch (error) {
        console.error('히스토리 로드 실패:', error);
      }
    };
    loadHistory();
  }, []);

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    setSelectedDataType(null);
    setResults(null);
  };

  const handleDataTypeSelect = (dataType: DataTypeConfig) => {
    setSelectedDataType(dataType);
    setResults(null);
  };

  const handleParamChange = (key: string, value: string) => {
    setApiParams(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleMetaChange = (path: string[], value: any) => {
    setQualityMeta(prev => {
      const newMeta = JSON.parse(JSON.stringify(prev));
      let current = newMeta;
      
      for (let i = 0; i < path.length - 1; i++) {
        if (!current[path[i]]) {
          current[path[i]] = {};
        }
        current = current[path[i]];
      }
      
      current[path[path.length - 1]] = value;
      return newMeta;
    });
  };

  const handleRunQualityCheck = async () => {
    if (!selectedDataType) return;
    
    setIsRunning(true);
    try {
      const result = await runQualityCheck({
        data_type: selectedDataType.id,
        api_params: apiParams,
        quality_meta: qualityMeta
      });
      
      setResults(result);
      setActiveTab('results');
      
      // 히스토리 새로고침
      const historyData = await getQualityCheckHistory();
      setHistory(historyData);
    } catch (error) {
      console.error('품질 검사 실행 실패:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const renderParamInput = (key: string, value: string | number) => (
    <div key={key} className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {key}
      </label>
      <input
        type="text"
        value={String(value)}
        onChange={(e) => handleParamChange(key, e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );

  const renderMetaInput = (obj: any, path: string[] = []): React.ReactNode => {
    return Object.entries(obj).map(([key, value]) => {
      const currentPath = [...path, key];
      
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        return (
          <div key={key} className="ml-4 mb-4">
            <h4 className="text-sm font-semibold text-gray-600 mb-2">{key}</h4>
            {renderMetaInput(value, currentPath)}
          </div>
        );
      } else if (Array.isArray(value)) {
        return (
          <div key={key} className="ml-4 mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {key} (쉼표로 구분)
            </label>
            <input
              type="text"
              value={Array.isArray(value) ? value.join(', ') : String(value)}
              onChange={(e) => handleMetaChange(currentPath, e.target.value.split(',').map(s => s.trim()))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        );
      } else {
        return (
          <div key={key} className="ml-4 mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {key}
            </label>
            <input
              type="text"
              value={String(value)}
              onChange={(e) => handleMetaChange(currentPath, e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        );
      }
    });
  };

  return (
    <div className="dashboard-layout">
      <Sidebar currentPage={currentPage} onPageChange={onPageChange} />
      <div className="dashboard-main-area">
        <div className="flex gap-8">
          <div className="dashboard-main-content">
            <div className="dashboard-top-tabs">
              <TopTabs currentPage={currentPage} onPageChange={onPageChange} />
            </div>
            
            {/* 품질 검사 헤더 */}
            <div className="bg-white shadow-sm border-b mb-6">
              <div className="px-6 py-4">
                <h1 className="text-2xl font-bold text-gray-900">데이터 품질 검사</h1>
                <p className="text-gray-600 mt-1">25가지 데이터 타입에 대한 품질 검사를 수행합니다</p>
              </div>
            </div>

            <div className="px-6 py-6">
              {/* 데이터 타입 선택 드롭다운 */}
              <div className="bg-white rounded-lg shadow-sm border p-6 mb-6 w-1/2">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">데이터 타입 선택</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* 첫 번째 드롭다운: 카테고리 선택 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      카테고리 선택
                    </label>
                    <select
                      value={selectedCategory}
                      onChange={(e) => handleCategorySelect(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">카테고리를 선택하세요</option>
                      {Object.keys(DATA_TYPES_BY_CATEGORY).map((category) => {
                        const dataTypes = DATA_TYPES_BY_CATEGORY[category];
                        const dataTypeNames = dataTypes.length > 3 
                          ? dataTypes.slice(0, 3).map(dt => dt.name).join(', ') + '...'
                          : dataTypes.map(dt => dt.name).join(', ');
                        return (
                          <option key={category} value={category}>
                            {category} ({dataTypeNames})
                          </option>
                        );
                      })}
                    </select>
                  </div>

                  {/* 두 번째 드롭다운: 데이터 타입 선택 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      데이터 타입 선택
                    </label>
                    <select
                      value={selectedDataType?.id || ''}
                      onChange={(e) => {
                        const dataType = DATA_TYPES.find(dt => dt.id === e.target.value);
                        if (dataType) {
                          handleDataTypeSelect(dataType);
                        }
                      }}
                      disabled={!selectedCategory}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                    >
                      <option value="">데이터 타입을 선택하세요</option>
                      {selectedCategory && DATA_TYPES_BY_CATEGORY[selectedCategory]?.map((dataType) => (
                        <option key={dataType.id} value={dataType.id}>
                          {dataType.name} - {dataType.description}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* 선택된 데이터 타입 정보 표시 */}
                {selectedDataType && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-md">
                    <h3 className="font-medium text-blue-900">{selectedDataType.name}</h3>
                    <p className="text-sm text-blue-700">{selectedDataType.description}</p>
                    <p className="text-xs text-blue-600 mt-1">카테고리: {selectedDataType.category}</p>
                  </div>
                )}
              </div>

              <div className="grid grid-cols-1 gap-6">
                {/* 설정 및 실행 */}
                  {selectedDataType ? (
                    <div className="space-y-6">
                      {/* 탭 네비게이션 */}
                      <div className="bg-white rounded-lg shadow-sm border">
                        <div className="flex border-b">
                          <button
                            onClick={() => setActiveTab('config')}
                            className={`px-6 py-3 text-sm font-medium ${
                              activeTab === 'config'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                          >
                            설정
                          </button>
                          <button
                            onClick={() => setActiveTab('results')}
                            className={`px-6 py-3 text-sm font-medium ${
                              activeTab === 'results'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                          >
                            결과
                          </button>
                          <button
                            onClick={() => setActiveTab('history')}
                            className={`px-6 py-3 text-sm font-medium ${
                              activeTab === 'history'
                                ? 'text-blue-600 border-b-2 border-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                          >
                            히스토리
                          </button>
                        </div>
                      </div>

                      {/* 탭 컨텐츠 */}
                      {activeTab === 'config' && (
                        <div>
                          <div className="space-y-4">
                            {/* API 파라미터 설정과 설명 */}
                            <div className="flex gap-4">
                              {/* API 파라미터 설정 */}
                              <div className="w-1/2">
                                <div className="bg-white rounded-lg shadow-sm border p-4">
                                  <h2 className="text-lg font-semibold text-gray-900 mb-3">API 파라미터 설정</h2>
                                  <textarea
                                    value={JSON.stringify(apiParams, null, 2)}
                                    onChange={(e) => {
                                      try {
                                        const parsed = JSON.parse(e.target.value);
                                        setApiParams(parsed);
                                      } catch (error) {
                                        // JSON 파싱 오류 시 무시
                                      }
                                    }}
                                    rows={10}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                                    placeholder="API 파라미터를 JSON 형태로 입력하세요"
                                  />
                                </div>
                              </div>

                              {/* API 파라미터 설명 */}
                              <div className="w-1/2">
                                <div className="bg-blue-50 rounded-lg p-4">
                                  <h3 className="text-lg font-semibold text-blue-900 mb-3">
                                    {getApiParameterDescription(selectedDataType)?.title || 'API 파라미터'}
                                  </h3>
                                  <div className="space-y-3 text-sm text-blue-800 text-left">
                                    <p><strong>파라미터 상세:</strong></p>
                                    <div className="space-y-2">
                                      {getApiParameterDescription(selectedDataType)?.parameters.map((param, index) => (
                                        <div key={index} className="flex items-start space-x-2">
                                          <code className="bg-white px-2 py-1 rounded text-xs font-mono w-20 text-center">{param.code}</code>
                                          <div className="text-xs">
                                            <div><strong>{param.name}</strong> ({param.required ? '필수' : '선택'}, {param.type})</div>
                                            {'format' in param && param.format && <div className="text-gray-600 ml-2">형식: {param.format}</div>}
                                            <div className="text-gray-600 ml-2">예: {param.example}</div>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                    {getApiParameterDescription(selectedDataType)?.note && (
                                      <div className="bg-yellow-100 p-2 rounded text-xs">
                                        <strong>주의:</strong> {getApiParameterDescription(selectedDataType)?.note}
                                      </div>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>

                            {/* 품질 검사 규칙 설정과 설명 */}
                            <div className="flex gap-4">
                              {/* 품질 검사 메타데이터 설정 */}
                              <div className="w-1/2">
                                <div className="bg-white rounded-lg shadow-sm border p-4">
                                  <h2 className="text-lg font-semibold text-gray-900 mb-3">품질 검사 규칙 설정</h2>
                                  
                                  {/* 탭 메뉴 */}
                                  <div className="flex space-x-1 mb-4 border-b border-gray-200">
                                    {[
                                      { key: 'DV', label: '유효성 검사', color: 'blue' },
                                      { key: 'DC', label: '일관성 검사', color: 'green' },
                                      { key: 'DU', label: '사용성 검사', color: 'purple' },
                                      { key: 'DT', label: '적시성 검사', color: 'orange' },
                                      { key: 'DI', label: '완전성 검사', color: 'red' }
                                    ].map((tab) => (
                                      <button
                                        key={tab.key}
                                        onClick={() => setQualityRuleTab(tab.key as any)}
                                        className={`px-3 py-2 text-sm font-medium rounded-t-lg transition-colors ${
                                          qualityRuleTab === tab.key
                                            ? `bg-${tab.color}-100 text-${tab.color}-700 border-b-2 border-${tab.color}-500`
                                            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                                        }`}
                                      >
                                        {tab.label}
                                      </button>
                                    ))}
                                  </div>

                                  {/* 탭 내용 */}
                                  <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                      {qualityRuleTab} 규칙 설정
                                    </label>
                                    <textarea
                                      value={JSON.stringify(qualityMeta[qualityRuleTab] || {}, null, 2)}
                                      onChange={(e) => {
                                        try {
                                          const parsed = JSON.parse(e.target.value);
                                          setQualityMeta(prev => ({
                                            ...prev,
                                            [qualityRuleTab]: parsed
                                          }));
                                        } catch (error) {
                                          // JSON 파싱 오류 시 무시
                                        }
                                      }}
                                      rows={15}
                                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                                      placeholder={`${qualityRuleTab} 규칙을 JSON 형태로 입력하세요`}
                                    />
                                  </div>
                                </div>
                              </div>

                              {/* 품질 검사 규칙 설명 */}
                              <div className="w-1/2">
                                <div className="bg-green-50 rounded-lg p-4">
                                  <h3 className="text-lg font-semibold text-green-900 mb-3">
                                    {getQualityRuleDescription(selectedDataType)?.title || '품질 검사 규칙'}
                                  </h3>
                                  <div className="space-y-3 text-sm text-green-800 text-left">
                                    <div className="space-y-2">
                                      {getQualityRuleDescription(selectedDataType)?.rules.map((rule, index) => (
                                        <div key={index} className="flex items-start space-x-2">
                                          <code className="bg-white px-2 py-1 rounded text-xs font-mono">{rule.code}</code>
                                          <div className="text-xs">
                                            <div><strong>{rule.name}</strong></div>
                                            {rule.subRules.map((subRule, subIndex) => (
                                              <div key={subIndex}>
                                                <div className="text-gray-600">• {subRule.name}: {subRule.description}</div>
                                                {subRule.details.map((detail, detailIndex) => (
                                                  <div key={detailIndex} className="text-gray-500 ml-2">- {detail}</div>
                                                ))}
                                              </div>
                                            ))}
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>

                          {/* 실행 버튼 */}
                          <div className="bg-white rounded-lg shadow-sm border p-4 mt-6">
                            <div className="flex items-center justify-between">
                              <div>
                                <h2 className="text-lg font-semibold text-gray-900">품질 검사 실행</h2>
                                <p className="text-gray-600 mt-1">
                                  {selectedDataType.name} 데이터에 대한 품질 검사를 실행합니다
                                </p>
                              </div>
                              <button
                                onClick={handleRunQualityCheck}
                                disabled={isRunning}
                                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                {isRunning ? '실행 중...' : '품질 검사 실행'}
                              </button>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* 결과 탭 */}
                      {activeTab === 'results' && (
                        <div className="space-y-6">
                          {results ? (
                            <div className="bg-white rounded-lg shadow-sm border p-6">
                              <h2 className="text-lg font-semibold text-gray-900 mb-4">검사 결과</h2>
                              
                              {/* 요약 정보 */}
                              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                                <div className="bg-blue-50 p-4 rounded-lg">
                                  <div className="text-sm text-blue-600 font-medium">전체 검사</div>
                                  <div className="text-2xl font-bold text-blue-900">{results.results?.total_checks || 0}</div>
                                </div>
                                <div className="bg-green-50 p-4 rounded-lg">
                                  <div className="text-sm text-green-600 font-medium">통과</div>
                                  <div className="text-2xl font-bold text-green-900">{results.results?.total_passed || 0}</div>
                                </div>
                                <div className="bg-red-50 p-4 rounded-lg">
                                  <div className="text-sm text-red-600 font-medium">실패</div>
                                  <div className="text-2xl font-bold text-red-900">{(results.results?.total_checks || 0) - (results.results?.total_passed || 0)}</div>
                                </div>
                                <div className="bg-purple-50 p-4 rounded-lg">
                                  <div className="text-sm text-purple-600 font-medium">품질 점수</div>
                                  <div className="text-2xl font-bold text-purple-900">{results.results?.overall_rate?.toFixed(1) || 0}%</div>
                                </div>
                              </div>

                              {/* 검사 결과 상세 */}
                              <div className="space-y-4">
                                <h3 className="text-md font-semibold text-gray-800">검사 상세 결과</h3>
                                <div className="space-y-2">
                                  {results.results?.breakdown && Object.entries(results.results.breakdown).map(([checkType, result], index) => (
                                    <div key={index} className={`p-3 rounded-md border-l-4 ${
                                      result.status === 'PASS' ? 'bg-green-50 border-green-400' :
                                      result.status === 'FAIL' ? 'bg-red-50 border-red-400' :
                                      'bg-yellow-50 border-yellow-400'
                                    }`}>
                                      <div className="flex items-center justify-between">
                                        <div>
                                          <div className="font-medium text-gray-900">{checkType} 검사</div>
                                          <div className="text-sm text-gray-600">
                                            통과율: {result.pass_rate.toFixed(1)}%
                                          </div>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                            result.status === 'PASS' ? 'bg-green-100 text-green-800' :
                                            result.status === 'FAIL' ? 'bg-red-100 text-red-800' :
                                            'bg-yellow-100 text-yellow-800'
                                          }`}>
                                            {result.status}
                                          </span>
                                          <span className="text-sm text-gray-500">
                                            {result.total_checks}개 검사 중 {result.total_checks - result.failed_checks}개 통과
                                          </span>
                                        </div>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
                              <div className="text-gray-400 mb-4">
                                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                              </div>
                              <h3 className="text-lg font-medium text-gray-900 mb-2">검사 결과가 없습니다</h3>
                              <p className="text-gray-600">품질 검사를 실행하면 결과가 여기에 표시됩니다.</p>
                            </div>
                          )}
                        </div>
                      )}

                      {/* 히스토리 탭 */}
                      {activeTab === 'history' && (
                        <div className="space-y-6">
                          <div className="bg-white rounded-lg shadow-sm border p-6">
                            <h2 className="text-lg font-semibold text-gray-900 mb-4">검사 히스토리</h2>
                            
                            {history.length > 0 ? (
                              <div className="space-y-4">
                                {history.map((item, index) => (
                                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                                    <div className="flex items-center justify-between">
                                      <div>
                                        <div className="font-medium text-gray-900">{item.data_type}</div>
                                        <div className="text-sm text-gray-600">검사 ID: {item.id}</div>
                                        <div className="text-xs text-gray-500">
                                          {new Date(item.created_at).toLocaleString('ko-KR')}
                                        </div>
                                      </div>
                                      <div className="flex items-center space-x-4">
                                        <div className="text-right">
                                          <div className="text-sm text-gray-600">상태</div>
                                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                            item.status === 'PASS' ? 'bg-green-100 text-green-800' :
                                            item.status === 'FAIL' ? 'bg-red-100 text-red-800' :
                                            'bg-yellow-100 text-yellow-800'
                                          }`}>
                                            {item.status === 'PASS' ? '양호' :
                                             item.status === 'FAIL' ? '주의' : '실행중'}
                                          </span>
                                        </div>
                                        {item.results && (
                                          <div className="text-right">
                                            <div className="text-sm text-gray-600">품질점수</div>
                                            <div className="font-medium">
                                              {item.results.overall_rate?.toFixed(1) || 0}%
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div className="text-center py-8">
                                <div className="text-gray-400 mb-4">
                                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                  </svg>
                                </div>
                                <h3 className="text-lg font-medium text-gray-900 mb-2">검사 히스토리가 없습니다</h3>
                                <p className="text-gray-600">아직 실행된 품질 검사가 없습니다.</p>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
                      <div className="text-gray-400 mb-4">
                        <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">데이터 타입을 선택하세요</h3>
                      <p className="text-gray-600">왼쪽에서 검사할 데이터 타입을 선택하면 설정을 시작할 수 있습니다.</p>
                    </div>
                  )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QualityCheckPage;
