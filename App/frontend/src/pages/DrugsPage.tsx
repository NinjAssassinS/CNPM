import { useEffect, useState, useCallback } from 'react';
import { Search, Pill, ExternalLink, Loader2 } from 'lucide-react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import DrugCard from '@/components/DrugCard';
import client from '@/lib/client';
import { api } from '@/lib/client';

const DrugsPage = () => {
  const [drugs, setDrugs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGroup, setSelectedGroup] = useState('');
  const [fdaResults, setFdaResults] = useState<any[]>([]);
  const [fdaLoading, setFdaLoading] = useState(false);
  const [showFDAResults, setShowFDAResults] = useState(false);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    const fetchDrugs = async () => {
      try {
        const response = await client.entities.drugs.query({ limit: 1000 });
        setDrugs(response.data?.items || []);
      } catch (err) {
        console.error('Failed to fetch drugs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDrugs();
  }, []);

  const searchFDA = useCallback(async (query: string) => {
    if (!query.trim()) {
      setFdaResults([]);
      setShowFDAResults(false);
      return;
    }
    setFdaLoading(true);
    setShowFDAResults(true);
    try {
      const res = await api.get('/api/v1/openfda/label', {
        params: { search: `openfda.brand_name:${query} OR openfda.generic_name:${query}`, limit: 9 },
        timeout: 10000,
      });
      const results = res.data?.results || [];
      setFdaResults(results.map((r: any) => {
        const openfda = r.openfda || {};
        return {
          id: `fda-${openfda.spl_id?.[0] || Math.random()}`,
          name: openfda.brand_name?.[0] || openfda.generic_name?.[0] || query,
          generic_name: openfda.generic_name?.[0] || '',
          manufacturer: openfda.manufacturer_name?.[0] || 'FDA',
          group_name: 'FDA',
          price: '',
          rating: 0,
          usage_info: r.indications_and_usage?.[0] || r.purpose?.[0] || '',
          code: openfda.product_ndc?.[0] || '',
          isFDA: true,
          spl_id: openfda.spl_id?.[0],
        };
      }));
    } catch {
      setFdaResults([]);
    } finally {
      setFdaLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery && !loading) searchFDA(searchQuery);
    }, 600);
    return () => clearTimeout(timer);
  }, [searchQuery, loading, searchFDA]);

  useEffect(() => {
    const fetchSaved = async () => {
      try {
        const res = await api.get('/api/v1/user/saved-drugs');
        const items = res.data?.items || [];
        setSavedIds(new Set(items.map((item: any) => item.drug_id)));
      } catch {
        // not logged in
      }
    };
    fetchSaved();
  }, []);

  const toggleSaveDrug = async (drugId: number | string) => {
    const numericId = Number(drugId);
    try {
      if (savedIds.has(numericId)) {
        await api.delete(`/api/v1/user/saved-drugs/${numericId}`);
        setSavedIds((prev) => { const next = new Set(prev); next.delete(numericId); return next; });
      } else {
        await api.post(`/api/v1/user/saved-drugs/${numericId}`);
        setSavedIds((prev) => new Set(prev).add(numericId));
      }
    } catch {
      console.error('Failed to toggle save drug');
    }
  };

  const groups = [...new Set(drugs.map((d) => d.group_name).filter(Boolean))];

  const filteredDrugs = drugs.filter((drug) => {
    const matchesSearch =
      !searchQuery ||
      drug.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      drug.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      drug.manufacturer?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesGroup = !selectedGroup || drug.group_name === selectedGroup;
    return matchesSearch && matchesGroup;
  });

  return (
    <div className="min-h-screen bg-slate-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-slate-900">Danh mục thuốc</h1>
          <p className="text-slate-500 text-sm mt-1">Tra cứu thông tin chi tiết về các loại thuốc</p>
        </div>

        {/* Search & Filter */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm thuốc theo tên, mã, nhà sản xuất..."
              className="w-full h-12 pl-11 pr-4 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            />
          </div>
          <select
            value={selectedGroup}
            onChange={(e) => setSelectedGroup(e.target.value)}
            className="h-12 px-4 border border-slate-200 rounded-xl text-sm bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tất cả nhóm</option>
            {groups.map((g) => (
              <option key={g} value={g}>{g}</option>
            ))}
          </select>
        </div>

        {/* FDA Search Results */}
        {showFDAResults && searchQuery && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <Pill className="h-5 w-5 text-emerald-600" />
              <h2 className="text-lg font-semibold text-slate-900">Kết quả từ FDA</h2>
              <a href="https://www.fda.gov/drugs" target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline flex items-center gap-1 ml-auto">
                Nguồn: FDA <ExternalLink className="h-3 w-3" />
              </a>
            </div>
            {fdaLoading ? (
              <div className="flex items-center gap-2 text-sm text-slate-500 py-4">
                <Loader2 className="h-4 w-4 animate-spin" /> Đang tìm kiếm từ FDA...
              </div>
            ) : fdaResults.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                {fdaResults.map((drug) => (
                  <div key={drug.id} className="bg-white border border-emerald-200 rounded-2xl p-5 hover:shadow-lg hover:border-emerald-300 transition-all duration-300 flex flex-col h-full relative">
                    <div className="absolute top-3 right-3">
                      <span className="px-2 py-0.5 bg-emerald-50 text-emerald-600 text-xs rounded-full font-medium">FDA</span>
                    </div>
                    <div className="flex items-start gap-4">
                      <div className="w-14 h-14 rounded-xl bg-emerald-50 flex items-center justify-center text-2xl flex-shrink-0">💊</div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold text-slate-900 text-sm">{drug.name}</h4>
                        {drug.generic_name && <p className="text-xs text-slate-500 mt-0.5">{drug.generic_name}</p>}
                        <p className="text-xs text-slate-400 mt-0.5">{drug.manufacturer}</p>
                        {drug.usage_info && (
                          <p className="text-xs text-slate-600 mt-2 line-clamp-2">{drug.usage_info}</p>
                        )}
                        <a
                          href={`https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=${drug.spl_id}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 mt-3 text-blue-600 text-xs font-medium hover:underline"
                        >
                          Xem trên DailyMed <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500 py-4">Không tìm thấy kết quả từ FDA</p>
            )}
          </div>
        )}

        {/* Results */}
        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
          </div>
        ) : filteredDrugs.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-2xl border border-slate-200">
            <Search className="h-12 w-12 text-slate-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-slate-900 mb-2">Không tìm thấy thuốc</h3>
            <p className="text-sm text-slate-500">Thử thay đổi từ khóa tìm kiếm</p>
          </div>
        ) : (
          <>
            <p className="text-sm text-slate-500 mb-4">
              Tìm thấy <span className="font-semibold text-slate-900">{filteredDrugs.length}</span> loại thuốc
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {filteredDrugs.map((drug) => (
                <DrugCard key={drug.id} drug={drug} isSaved={savedIds.has(Number(drug.id))} onSaveToggle={toggleSaveDrug} />
              ))}
            </div>
          </>
        )}
      </div>
      <Footer />
    </div>
  );
};

export default DrugsPage;