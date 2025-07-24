/**
 * Demo Component showcasing all new enterprise components
 */

import React, { useState } from 'react';
import {
  CodeEditor,
  DataTable,
  LineChart,
  BarChart,
  PieChart,
  Modal,
  ConfirmModal,
  useModal,
  useToast,
  Button,
  Card,
  CardHeader,
  CardContent,
  type Column,
} from '../../shared/components';

// Sample data
const sampleXmlCode = `<?xml version="1.0" encoding="UTF-8"?>
<streamworks-config>
  <data-sources>
    <data-source id="db1" type="postgresql">
      <connection-string>postgresql://user:pass@localhost:5432/db</connection-string>
      <schema>public</schema>
    </data-source>
  </data-sources>
  <transformations>
    <mapping source="customers" target="users">
      <field source="customer_id" target="user_id" />
      <field source="name" target="full_name" />
    </mapping>
  </transformations>
</streamworks-config>`;

const sampleTableData = [
  { id: 1, name: 'Document 1', type: 'PDF', size: '2.4 MB', date: '2024-01-15', status: 'processed' },
  { id: 2, name: 'Document 2', type: 'DOCX', size: '1.2 MB', date: '2024-01-14', status: 'processing' },
  { id: 3, name: 'Document 3', type: 'TXT', size: '0.5 MB', date: '2024-01-13', status: 'failed' },
  { id: 4, name: 'Document 4', type: 'PDF', size: '3.1 MB', date: '2024-01-12', status: 'processed' },
  { id: 5, name: 'Document 5', type: 'XLSX', size: '2.8 MB', date: '2024-01-11', status: 'processed' },
];

const tableColumns: Column[] = [
  { id: 'name', header: 'Name', accessorKey: 'name', sortable: true, filterable: true },
  { id: 'type', header: 'Type', accessorKey: 'type', sortable: true, filterable: true },
  { id: 'size', header: 'Size', accessorKey: 'size', sortable: true, align: 'right' },
  { id: 'date', header: 'Date', accessorKey: 'date', sortable: true },
  { 
    id: 'status', 
    header: 'Status', 
    accessorKey: 'status',
    cell: ({ getValue }) => {
      const status = getValue() as string;
      const colors = {
        processed: 'bg-green-100 text-green-800',
        processing: 'bg-blue-100 text-blue-800',
        failed: 'bg-red-100 text-red-800',
      };
      return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status as keyof typeof colors]}`}>
          {status}
        </span>
      );
    }
  },
];

const chartData = [
  { name: 'Jan', users: 400, documents: 240, queries: 120 },
  { name: 'Feb', users: 300, documents: 139, queries: 221 },
  { name: 'Mar', users: 200, documents: 980, queries: 229 },
  { name: 'Apr', users: 278, documents: 390, queries: 200 },
  { name: 'May', users: 189, documents: 480, queries: 218 },
  { name: 'Jun', users: 239, documents: 380, queries: 250 },
];

const pieData = [
  { name: 'PDF', value: 400, fill: '#FF6B35' },
  { name: 'DOCX', value: 300, fill: '#F7931E' },
  { name: 'TXT', value: 200, fill: '#FFD23F' },
  { name: 'XLSX', value: 100, fill: '#06FFA5' },
];

export function EnterpriseComponentsDemo() {
  const [xmlCode, setXmlCode] = useState(sampleXmlCode);
  const [selectedRows, setSelectedRows] = useState<any[]>([]);
  
  const modal = useModal();
  const confirmModal = useModal();
  const toast = useToast();

  const handleCodeChange = (value: string) => {
    setXmlCode(value);
  };

  const showToastExamples = () => {
    toast.success('This is a success message!');
    setTimeout(() => toast.info('This is an info message'), 500);
    setTimeout(() => toast.warning('This is a warning message'), 1000);
    setTimeout(() => toast.error('This is an error message'), 1500);
  };

  const showLoadingToast = () => {
    const loadingId = toast.loading('Processing request...');
    
    setTimeout(() => {
      toast.dismiss(loadingId);
      toast.success('Request completed successfully!');
    }, 3000);
  };

  const handleExport = (data: any[], format: string) => {
    toast.info(`Exporting ${data.length} rows as ${format.toUpperCase()}`);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
          Enterprise Components Demo
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400">
          Showcase of all advanced enterprise-grade components
        </p>
      </div>

      {/* Code Editor Demo */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">Monaco Code Editor</h2>
          <p className="text-neutral-600 dark:text-neutral-400">
            Full-featured code editor with syntax highlighting and StreamWorks XML support
          </p>
        </CardHeader>
        <CardContent>
          <CodeEditor
            language="xml"
            value={xmlCode}
            onChange={handleCodeChange}
            height="300px"
            showMinimap={true}
            exportable={true}
            placeholder="Enter your StreamWorks XML configuration here..."
          />
          <div className="mt-4 flex space-x-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setXmlCode('')}
            >
              Clear
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => setXmlCode(sampleXmlCode)}
            >
              Reset to Sample
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* DataTable Demo */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-semibold">Advanced DataTable</h2>
          <p className="text-neutral-600 dark:text-neutral-400">
            Sortable, filterable, and selectable table with pagination and export
          </p>
        </CardHeader>
        <CardContent>
          <DataTable
            data={sampleTableData}
            columns={tableColumns}
            selectable="multiple"
            exportable={true}
            onRowSelect={setSelectedRows}
            onExport={handleExport}
            expandableRows={true}
            renderExpandedRow={(row) => (
              <div className="p-4 space-y-2">
                <h4 className="font-medium">Document Details</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div><strong>ID:</strong> {row.id}</div>
                  <div><strong>Full Name:</strong> {row.name}</div>
                  <div><strong>File Type:</strong> {row.type}</div>
                  <div><strong>File Size:</strong> {row.size}</div>
                  <div><strong>Upload Date:</strong> {row.date}</div>
                  <div><strong>Status:</strong> {row.status}</div>
                </div>
              </div>
            )}
          />
          {selectedRows.length > 0 && (
            <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg">
              <p className="text-sm text-blue-700 dark:text-blue-300">
                {selectedRows.length} row(s) selected: {selectedRows.map(row => row.name).join(', ')}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Charts Demo */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Line Chart</h2>
          </CardHeader>
          <CardContent>
            <LineChart
              data={chartData}
              xKey="name"
              yKeys={['users', 'documents']}
              title="User Activity & Documents"
              exportable={true}
              height={250}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Bar Chart</h2>
          </CardHeader>
          <CardContent>
            <BarChart
              data={chartData}
              xKey="name"
              yKeys={['queries']}
              title="Monthly Queries"
              exportable={true}
              height={250}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Pie Chart</h2>
          </CardHeader>
          <CardContent>
            <PieChart
              data={pieData}
              dataKey="value"
              nameKey="name"
              valueKey="value"
              title="Document Types Distribution"
              exportable={true}
              height={250}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">Interactive Features</h2>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-medium mb-2">Modal System</h3>
              <div className="space-x-2">
                <Button onClick={modal.openModal}>
                  Open Modal
                </Button>
                <Button 
                  variant="outline" 
                  onClick={confirmModal.openModal}
                >
                  Confirm Dialog
                </Button>
              </div>
            </div>

            <div>
              <h3 className="font-medium mb-2">Toast Notifications</h3>
              <div className="space-x-2">
                <Button onClick={showToastExamples}>
                  Show Toast Examples
                </Button>
                <Button 
                  variant="outline" 
                  onClick={showLoadingToast}
                >
                  Loading Toast
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Modals */}
      <Modal
        isOpen={modal.isOpen}
        onClose={modal.closeModal}
        title="Sample Modal"
        size="lg"
        footer={
          <>
            <Button variant="ghost" onClick={modal.closeModal}>
              Cancel
            </Button>
            <Button onClick={modal.closeModal}>
              Confirm
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <p>This is a sample modal with advanced features:</p>
          <ul className="list-disc list-inside space-y-1 text-sm text-neutral-600 dark:text-neutral-400">
            <li>Accessible focus management</li>
            <li>Escape key and backdrop close</li>
            <li>Smooth animations</li>
            <li>Fullscreen toggle</li>
            <li>Portal rendering</li>
          </ul>
          <div className="p-4 bg-neutral-100 dark:bg-neutral-800 rounded-lg">
            <p className="text-sm">
              This modal demonstrates the glassmorphism effect and proper z-index handling.
            </p>
          </div>
        </div>
      </Modal>

      <ConfirmModal
        isOpen={confirmModal.isOpen}
        onClose={confirmModal.closeModal}
        onConfirm={() => {
          toast.success('Action confirmed!');
          confirmModal.closeModal();
        }}
        title="Confirm Action"
        message="Are you sure you want to perform this action? This cannot be undone."
        variant="warning"
        confirmText="Yes, Continue"
        cancelText="Cancel"
      />
    </div>
  );
}