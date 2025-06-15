import { Link } from "react-router-dom";
import { testCases } from "./testCases";

export default function TestMenu() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Test Cases</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {testCases.map((test) => (
            <Link
              key={test.id}
              to={`/test/${test.id}`}
              className="block p-6 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors">
              <h2 className="text-xl font-semibold mb-2">{test.name}</h2>
              <p className="text-gray-400">/test/{test.id}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
