import { useState } from "react";
import { AuthProvider, useAuth } from "./context/AuthContext";
import { LoginForm } from "./components/LoginForm";
import { Layout } from "./components/Layout";
import { Dashboard } from "./components/Dashboard";
import { InventoryManager } from "./components/InventoryManager";
import { PurchaseOrderManager } from "./components/PurchaseOrderManager";
import { RecipeManager } from "./components/RecipeManager";
import { ProductManager } from "./components/ProductManager";
import { SupplierManager } from "./components/SupplierManager";
import { UserManager } from "./components/UserManager";
import { AlertsManager } from "./components/AlertsManager";
import { ReportsManager } from "./components/ReportsManager";
import { SettingsManager } from "./components/SettingsManager";
import { SupplyEntryManager } from "./components/SupplyEntryManager";
import { SalesPointManager } from "./components/SalesPointManager";
import { TypewriterSplash } from './components/TypewriterSplash';
import { Toaster } from "./components/ui/sonner";

// Mapeo de páginas a módulos de permisos
const pageToModule: Record<string, string> = {
  'dashboard': 'DASHBOARD',
  'inventory': 'INSUMOS',
  'recipes': 'RECETAS',
  'purchase-orders': 'COMPRAS',
  'supply-entry': 'INVENTARIO',
  'products': 'PRODUCTOS',
  'suppliers': 'PROVEEDORES',
  'users': 'USUARIOS',
  'alerts': 'INVENTARIO',
  'reports': 'REPORTES',
  'settings': 'CONFIGURACION',
  'sales-point': 'VENTAS',
};

function AppContent() {
  const { user, isAuthenticated, isLoading, logout, canRead, isAdmin } = useAuth();
  const [currentPage, setCurrentPage] = useState("dashboard");
  const [showSplash, setShowSplash] = useState(true);

  const handleSplashEnd = () => {
    setShowSplash(false);
  };

  const handleLogout = () => {
    logout();
    setCurrentPage("dashboard");
    setShowSplash(true);
  };

  // Verificar si el usuario puede acceder a la página actual
  const canAccessPage = (page: string): boolean => {
    if (page === 'dashboard') return true; // Dashboard siempre accesible
    if (isAdmin()) return true; // Admin puede acceder a todo
    const modulo = pageToModule[page];
    return modulo ? canRead(modulo) : false;
  };

  // Cambiar de página solo si tiene permiso
  const handlePageChange = (page: string) => {
    if (canAccessPage(page)) {
      setCurrentPage(page);
    } else {
      // Si no tiene permiso, quedarse en dashboard
      setCurrentPage('dashboard');
    }
  };

  const renderCurrentPage = () => {
    // Verificar permiso antes de renderizar
    if (!canAccessPage(currentPage)) {
      return <Dashboard />;
    }

    switch (currentPage) {
      case "dashboard":
        return <Dashboard />;
      case "inventory":
        return <InventoryManager />;
      case "recipes":
        return <RecipeManager />;
      case "purchase-orders":
        return <PurchaseOrderManager />;
      case "supply-entry":
        return <SupplyEntryManager />;
      case "products":
        return <ProductManager />;
      case "suppliers":
        return <SupplierManager />;
      case "users":
        return <UserManager />;
      case "alerts":
        return <AlertsManager />;
      case "reports":
        return <ReportsManager />;
      case "settings":
        return <SettingsManager />;
      case "sales-point":
        return <SalesPointManager />;
      default:
        return <Dashboard />;
    }
  };

  if (showSplash) {
    return <TypewriterSplash onAnimationEnd={handleSplashEnd} />;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginForm />;
  }

  return (
    <>
      <Toaster position="top-right" richColors />
      <Layout
        currentPage={currentPage}
        onPageChange={handlePageChange}
        onLogout={handleLogout}
        username={user?.nombre || user?.email || ""}
      >
        {renderCurrentPage()}
      </Layout>
    </>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}