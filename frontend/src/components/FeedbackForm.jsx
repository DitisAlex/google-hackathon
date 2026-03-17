import { useState } from 'react';

export default function FeedbackForm({ repoUrl }) {
  const [rating, setRating] = useState(null); // 'accurate' | 'issues'
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e) {
    e.preventDefault();
    // TODO: wire up to POST /api/v1/feedback
    setSubmitted(true);
  }

  if (submitted) {
    return (
      <div className="rounded-2xl bg-gray-100 border border-gray-200 p-6 flex items-center gap-4">
        <span className="text-2xl">🙏</span>
        <div>
          <p className="font-semibold text-gray-800">Thanks for your feedback!</p>
          <p className="text-sm text-gray-500 mt-0.5">Your input helps us improve the analysis engine.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-gray-100 border border-gray-200 p-6">
      {/* Header row */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-6">
        <div>
          <h3 className="text-lg font-bold text-gray-900">Accuracy Feedback</h3>
          <p className="text-sm text-gray-500 mt-1 max-w-xs">
            Help us improve the analysis engine by rating this summary.
          </p>
        </div>
        {/* Rating buttons */}
        <div className="flex gap-3 flex-shrink-0">
          <button
            type="button"
            onClick={() => setRating('accurate')}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-semibold transition
              ${rating === 'accurate'
                ? 'bg-green-50 border-green-400 text-green-700'
                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300 hover:shadow-sm'}`}
          >
            <span className="text-lg">👍</span> Accurate
          </button>
          <button
            type="button"
            onClick={() => setRating('issues')}
            className={`flex items-center gap-2 px-5 py-3 rounded-xl border text-sm font-semibold transition
              ${rating === 'issues'
                ? 'bg-red-50 border-red-400 text-red-700'
                : 'bg-white border-gray-200 text-gray-700 hover:border-gray-300 hover:shadow-sm'}`}
          >
            <span className="text-lg">👎</span> Issues found
          </button>
        </div>
      </div>

      {/* Comment box */}
      <form onSubmit={handleSubmit}>
        <label className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">
          Model Improvement Comments
        </label>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Tell us how we can make the summary more accurate..."
          rows={4}
          className="w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-700
            placeholder-gray-400 resize-y focus:outline-none focus:ring-2 focus:ring-brand-500
            focus:border-transparent transition"
        />
        <div className="flex justify-end mt-4">
          <button
            type="submit"
            disabled={!rating && !comment.trim()}
            className="bg-gray-900 hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed
              text-white font-bold text-sm px-6 py-3 rounded-xl transition"
          >
            Submit Feedback
          </button>
        </div>
      </form>
    </div>
  );
}
