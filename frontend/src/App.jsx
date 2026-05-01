import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAuthStore } from './context/AuthContext'; // Ensure path matches your Zustand store

// Components & Pages
import Layout from './components/common/Layout';
import ApiStatusBanner from './components/common/ApiStatusBanner';
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import Home from './pages/public/Home';
import Products from './pages/public/Products';
import ProductDetail from './pages/public/ProductDetail';
import FarmerDashboard from './pages/farmer/Dashboard';
import FarmerProducts from './pages/farmer/Products';
import AddProduct from './pages/farmer/AddProduct';
import FarmerOrders from './pages/farmer/Orders';
import FarmerClaims from './pages/farmer/Claims';
import BuyerDashboard from './pages/buyer/Dashboard';
import BuyerOrders from './pages/buyer/Orders';
import AdminDashboard from './pages/admin/Dashboard';

const queryClient = new QueryClient();

// 1. Improved ProtectedRoute
function ProtectedRoute({ children, roles }) {
  const { isAuthenticated, user, isInitialized } = useAuthStore();
  
  // Wait for checkAuth to finish before making redirect decisions
  if (!isInitialized) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  if (roles && user && !roles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  
  return children;
}

function AppRoutes() {
  const checkAuth = useAuthStore((state) => state.checkAuth);
  const isInitialized = useAuthStore((state) => state.isInitialized);

  // 2. Run session check once on mount
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  // Prevent route flashing while verifying token
  if (!isInitialized) {
    return <div className="flex h-screen items-center justify-center">Verifying Session...</div>;
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="products" element={<Products />} />
        <Route path="products/:id" element={<ProductDetail />} />
      </Route>
      
      {/* Auth Routes - Prevent logged in users from seeing login/register */}
      <Route path="/login" element={<AuthPublicRoute><Login /></AuthPublicRoute>} />
      <Route path="/register" element={<AuthPublicRoute><Register /></AuthPublicRoute>} />
      
      {/* Farmer Routes */}
      <Route path="/farmer" element={
        <ProtectedRoute roles={['farmer']}>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/farmer/dashboard" replace />} />
        <Route path="dashboard" element={<FarmerDashboard />} />
        <Route path="products" element={<FarmerProducts />} />
        <Route path="products/add" element={<AddProduct />} />
        <Route path="orders" element={<FarmerOrders />} />
        <Route path="claims" element={<FarmerClaims />} />
      </Route>
      
      {/* Buyer Routes */}
      <Route path="/buyer" element={
        <ProtectedRoute roles={['buyer']}>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/buyer/dashboard" replace />} />
        <Route path="dashboard" element={<BuyerDashboard />} />
        <Route path="orders" element={<BuyerOrders />} />
      </Route>
      
      {/* Admin Routes */}
      <Route path="/admin" element={
        <ProtectedRoute roles={['admin']}>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/admin/dashboard" replace />} />
        <Route path="dashboard" element={<AdminDashboard />} />
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

// 3. Optional Helper: Prevent logged-in users from hitting /login
function AuthPublicRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? <Navigate to="/" replace /> : children;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ApiStatusBanner />
        <AppRoutes />
      </BrowserRouter>
    </QueryClientProvider>
  );
}