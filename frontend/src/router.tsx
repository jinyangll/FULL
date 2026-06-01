import { createBrowserRouter, redirect } from 'react-router-dom';
import App from './App';
import ErrorPage from './pages/ErrorPage';
import GuidePage from './pages/GuidePage';
import LoadingPage from './pages/LoadingPage';
import ProcessPage from './pages/ProcessPage';
import ReportPreviewPage from './pages/ReportPreviewPage';
import ReportPage from './pages/ReportPage';
import ServicePage from './pages/ServicePage';
import UploadPage from './pages/UploadPage';
import { getAnalysis, getPendingFilesMeta } from './lib/storage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <UploadPage /> },
      { path: 'service', element: <ServicePage /> },
      { path: 'process', element: <ProcessPage /> },
      { path: 'report-preview', element: <ReportPreviewPage /> },
      { path: 'guide', element: <GuidePage /> },
      {
        path: 'analyzing',
        loader: () => {
          if (getPendingFilesMeta().length === 0) {
            throw redirect('/');
          }
          return null;
        },
        element: <LoadingPage />,
      },
      {
        path: 'report',
        loader: () => {
          if (!getAnalysis()) {
            throw redirect('/');
          }
          return null;
        },
        element: <ReportPage />,
      },
      { path: 'error', element: <ErrorPage /> },
    ],
  },
]);
