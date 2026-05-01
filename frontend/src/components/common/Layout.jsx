import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../context/AuthContext';
import { Menu, X, User, LogOut, LayoutDashboard, Package, ShoppingCart, Shield } from 'lucide-react';
import { useState } from 'react';

export default function Layout() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center gap-2">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">P</span>
                </div>
                <span className="text-xl font-bold text-gray-900">Pre-Harvest</span>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-4">
              <Link 
                to="/products" 
                className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/products') ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'}`}
              >
                Browse Products
              </Link>
              
              {isAuthenticated ? (
                <div className="flex items-center gap-4">
                  {user?.role === 'farmer' && (
                    <>
                      <Link to="/farmer/dashboard" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/farmer') ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'}`}>
                        Dashboard
                      </Link>
                      <Link to="/farmer/products" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/farmer/products') ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'}`}>
                        My Products
                      </Link>
                      <Link to="/farmer/orders" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/farmer/orders') ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'}`}>
                        Orders
                      </Link>
                      <Link to="/farmer/claims" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/farmer/claims') ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'}`}>
                        Claims
                      </Link>
                    </>
                  )}
                  {user?.role === 'buyer' && (
                    <>
                      <Link to="/buyer/dashboard" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/buyer') ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'}`}>
                        Dashboard
                      </Link>
                      <Link to="/buyer/orders" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/buyer/orders') ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'}`}>
                        My Orders
                      </Link>
                    </>
                  )}
                  {user?.role === 'admin' && (
                    <Link to="/admin/dashboard" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/admin') ? 'text-primary-600' : 'text-gray-700 hover:text-primary-600'}`}>
                      Admin
                    </Link>
                  )}
                  
                  {/* User Menu */}
                  <div className="relative group">
                    <button className="flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-primary-600">
                      <User className="w-5 h-5" />
                      {user?.full_name}
                    </button>
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 hidden group-hover:block">
                      <button onClick={handleLogout} className="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                        <LogOut className="w-4 h-4" />
                        Logout
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Link to="/login" className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-primary-600">
                    Login
                  </Link>
                  <Link to="/register" className="px-4 py-2 text-sm font-medium bg-primary-600 text-white rounded-lg hover:bg-primary-700">
                    Register
                  </Link>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden flex items-center">
              <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="text-gray-700">
                {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t">
            <div className="px-4 py-2 space-y-2">
              <Link to="/products" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                Browse Products
              </Link>
              {isAuthenticated ? (
                <>
                  {user?.role === 'farmer' && (
                    <>
                      <Link to="/farmer/dashboard" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                        Farmer Dashboard
                      </Link>
                      <Link to="/farmer/products" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                        My Products
                      </Link>
                      <Link to="/farmer/orders" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                        Orders
                      </Link>
                      <Link to="/farmer/claims" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                        Claims
                      </Link>
                    </>
                  )}
                  {user?.role === 'buyer' && (
                    <>
                      <Link to="/buyer/dashboard" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                        Buyer Dashboard
                      </Link>
                      <Link to="/buyer/orders" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                        My Orders
                      </Link>
                    </>
                  )}
                  <button onClick={handleLogout} className="block w-full text-left px-3 py-2 text-red-600 hover:bg-gray-100 rounded-md">
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-md">
                    Login
                  </Link>
                  <Link to="/register" className="block px-3 py-2 text-primary-600 hover:bg-gray-100 rounded-md">
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            © 2024 Pre-Harvest Marketplace. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}