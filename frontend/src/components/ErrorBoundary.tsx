import React from "react";

interface Props {
    children?: React.ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
    state: State = {
        hasError: false,
        error: null,
    };

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error("Uncaught error:", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center bg-red-50 p-10">
                    <div className="max-w-4xl bg-white p-8 rounded-lg shadow-xl border border-red-200">
                        <h1 className="text-3xl font-bold text-red-600 mb-4">Application Crashed</h1>
                        <p className="mb-4 text-gray-700">Please share this error message with the developer:</p>
                        <div className="bg-slate-900 text-red-300 p-4 rounded overflow-auto max-h-[60vh] text-sm font-mono">
                            <p className="font-bold border-b border-white/10 pb-2 mb-2">{this.state.error?.toString()}</p>
                            <pre>{this.state.error?.stack}</pre>
                        </div>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
