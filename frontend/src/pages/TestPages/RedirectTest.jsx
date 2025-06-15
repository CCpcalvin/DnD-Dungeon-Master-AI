import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { testCases } from "./testCases";

export default function RedirectTest() {
  const { testCase } = useParams();
  const navigate = useNavigate();
  const [TestComponent, setTestComponent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadComponent = async () => {
      try {
        // Find the test case
        const test = testCases.find((tc) => tc.id === testCase);
        if (!test) {
          throw new Error(`Test case "${testCase}" not found`);
        }

        // Import the test component
        const module = await test.component();
        setTestComponent(() => module.default);
      } catch (err) {
        console.error("Error loading test component:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadComponent();
  }, [testCase, navigate]);

  if (loading) {
    return <div className="p-4">Loading test case...</div>;
  }

  if (error) {
    return (
      <div className="p-4 text-red-500">
        <h2 className="text-xl font-bold">Error</h2>
        <p>{error}</p>
        <button
          onClick={() => navigate("/test")}
          className="text-blue-400 hover:underline">
          Back to Test Menu
        </button>
      </div>
    );
  }

  return TestComponent ? <TestComponent /> : null;
}
