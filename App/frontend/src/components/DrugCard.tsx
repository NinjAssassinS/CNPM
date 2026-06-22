import { Link } from 'react-router-dom';
import { Star, Bookmark } from 'lucide-react';

interface Drug {
  id: number | string;
  name: string;
  group_name: string;
  manufacturer: string;
  rating: number;
  price: string;
  usage_info: string;
  code?: string;
  match_score?: number;
  data_source?: string;
}

interface DrugCardProps {
  drug: Drug;
  isSaved?: boolean;
  onSaveToggle?: (drugId: number | string) => void;
}

const DrugCard = ({ drug, isSaved, onSaveToggle }: DrugCardProps) => {
  const rating = drug.rating || 0;
  const fullStars = Math.floor(rating);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-lg hover:border-blue-200 transition-all duration-300 flex flex-col h-full">
      <div className="flex items-start gap-4">
        <div className="w-14 h-14 rounded-xl bg-blue-50 flex items-center justify-center text-2xl flex-shrink-0">
          💊
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h4 className="font-semibold text-slate-900 text-sm">{drug.name}</h4>
              <p className="text-xs text-slate-500 mt-0.5">{drug.manufacturer}</p>
            </div>
            <div className="flex gap-1.5">
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 whitespace-nowrap">
                {drug.group_name}
              </span>
              {drug.data_source === 'local' && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 whitespace-nowrap">
                  CSDL
                </span>
              )}
              {drug.data_source === 'openfda' && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 whitespace-nowrap">
                  openFDA
                </span>
              )}
            </div>
          </div>

          {drug.usage_info && (
            <p className="text-xs text-slate-600 mt-2 line-clamp-2">{drug.usage_info}</p>
          )}

          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className={`h-3 w-3 ${i < fullStars ? 'text-amber-400 fill-amber-400' : 'text-slate-200 fill-slate-200'}`}
                />
              ))}
              <span className="text-xs text-slate-500 ml-1">{rating.toFixed(1)}</span>
            </div>
            <span className="text-sm font-semibold text-blue-600">{drug.price}</span>
          </div>

          {drug.match_score && (
            <div className="mt-2">
              <span className="text-xs text-emerald-600 font-medium">{drug.match_score}% phù hợp</span>
            </div>
          )}

          <div className="flex gap-2 mt-3">
            <Link
              to={`/drug/${drug.id}`}
              className="flex-1 h-8 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center"
            >
              Xem chi tiết
            </Link>
            <button
              onClick={() => onSaveToggle?.(drug.id)}
              className={`h-8 w-8 border rounded-lg flex items-center justify-center transition-colors ${
                isSaved
                  ? 'border-blue-300 text-blue-600 bg-blue-50'
                  : 'border-slate-200 text-slate-400 hover:text-blue-600 hover:border-blue-300'
              }`}
            >
              <Bookmark className={`h-3.5 w-3.5 ${isSaved ? 'fill-blue-600' : ''}`} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DrugCard;