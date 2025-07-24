import { Component } from 'react';
import type { ReactNode, ErrorInfo } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Card, CardContent } from '@/shared/components/UI/Card';
import { Button } from '@/shared/components/UI/Button';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleReset = () => {
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
          <Card variant="elevated" className="max-w-lg w-full">
            <CardContent>
              <div className="text-center space-y-6">
                <div className="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center mx-auto">
                  <AlertTriangle size={32} className="text-red-600 dark:text-red-400" />
                </div>

                <div>
                  <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
                    Etwas ist schiefgelaufen
                  </h2>
                  <p className="text-neutral-600 dark:text-neutral-400 mb-4">
                    Ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es erneut.
                  </p>

                  {process.env['NODE_ENV'] === 'development' && this.state.error && (
                    <details className="text-left text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg mb-4">
                      <summary className="cursor-pointer font-medium mb-2">
                        Fehlerdetails (Development)
                      </summary>
                      <pre className="whitespace-pre-wrap overflow-auto">
                        {this.state.error.message}
                        {this.state.error.stack && `\n\n${this.state.error.stack}`}
                      </pre>
                    </details>
                  )}
                </div>

                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  <Button
                    variant="primary"
                    onClick={this.handleReset}
                    leftIcon={<RefreshCw size={16} />}
                  >
                    Erneut versuchen
                  </Button>
                  
                  <Button
                    variant="secondary"
                    onClick={this.handleReload}
                  >
                    Seite neu laden
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}