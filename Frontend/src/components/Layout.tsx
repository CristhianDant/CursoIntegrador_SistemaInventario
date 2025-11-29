import { ReactNode, useState, useEffect } from "react";
import { 
  Home, 
  Package, 
  AlertTriangle, 
  BarChart3, 
  Settings, 
  LogOut,
  Menu,
  X,
  ChefHat,
  User,
  Building,
  Wrench,
  Truck,
  Shield
} from "lucide-react";
import { Button } from "./ui/button";
import { cn } from "./ui/utils";
import { useAuth } from "../context/AuthContext";
import { Badge } from "./ui/badge";
// @ts-ignore: SVG module is handled by the bundler (svgr) and may not have TypeScript declarations
import MiLogo from './Img/Pasteleria.svg?react';

interface LayoutProps {
  children: ReactNode;
  currentPage: string;
  onPageChange: (page: string) => void;
  onLogout: () => void;
  username: string;
}

// Cada item de menú tiene un módulo de permisos requerido
const menuItems = [
  { id: 'dashboard', label: 'Dashboard', icon: Home, modulo: 'DASHBOARD' },
  { id: 'inventory', label: 'Insumos', icon: Package, modulo: 'INSUMOS' },
  { id: 'recipes', label: 'Recetas', icon: ChefHat, modulo: 'RECETAS' },
  { id: 'purchase-orders', label: 'Órdenes de Compra', icon: Wrench, modulo: 'COMPRAS' },
  { id: 'supply-entry', label: 'Ingreso de Insumos', icon: Truck, modulo: 'INVENTARIO' },
  { id: 'products', label: 'Productos', icon: Package, modulo: 'PRODUCTOS' },
  { id: 'suppliers', label: 'Proveedores', icon: Building, modulo: 'PROVEEDORES' },
  { id: 'users', label: 'Usuarios', icon: User, modulo: 'USUARIOS' },
  { id: 'alerts', label: 'Alertas', icon: AlertTriangle, modulo: 'INVENTARIO' },
  { id: 'reports', label: 'Reportes', icon: BarChart3, modulo: 'REPORTES' },
  { id: 'settings', label: 'Configuración', icon: Settings, modulo: 'CONFIGURACION' },
];

export function Layout({ children, currentPage, onPageChange, onLogout, username }: LayoutProps) {
  const { isAdmin, canRead, user } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [companyName, setCompanyName] = useState('Sistema de Inventario');

  // Filtrar menú según permisos del usuario
  // Admin ve todo, otros usuarios solo ven módulos donde tienen permiso (leer o escribir)
  const visibleMenuItems = menuItems.filter(item => {
    // Dashboard siempre visible para todos
    if (item.modulo === 'DASHBOARD') return true;
    // Admin ve todo
    if (isAdmin()) return true;
    // Otros usuarios solo ven módulos donde tienen permiso
    return canRead(item.modulo);
  });

  // Cargar nombre de empresa desde localStorage
  useEffect(() => {
    const savedCompanyName = localStorage.getItem('companyName');
    if (savedCompanyName) {
      setCompanyName(savedCompanyName);
    }

    // Escuchar evento personalizado de cambio de nombre de empresa
    const handleCompanyNameChange = (event: CustomEvent) => {
      setCompanyName(event.detail.companyName);
    };

    // Escuchar cambios en localStorage
    const handleStorageChange = () => {
      const updatedName = localStorage.getItem('companyName');
      if (updatedName) {
        setCompanyName(updatedName);
      }
    };

    window.addEventListener('companyNameChanged' as any, handleCompanyNameChange);
    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('companyNameChanged' as any, handleCompanyNameChange);
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-2">            <MiLogo className="h-13 w-13 text-white" />
            <span className="text-xl font-semibold text-gray-900">{companyName}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {visibleMenuItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onPageChange(item.id);
                  setSidebarOpen(false);
                }}
                className={cn(
                  "w-full flex items-center space-x-3 px-3 py-2 rounded-md text-left transition-colors",
                  currentPage === item.id
                    ? "bg-orange-100 text-orange-700"
                    : "text-gray-700 hover:bg-gray-100"
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="p-4 border-t">
          <div className="flex items-center justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">{username}</p>
              <div className="flex items-center gap-1 flex-wrap">
                {isAdmin() ? (
                  <Badge variant="default" className="text-xs bg-orange-500 hover:bg-orange-600">
                    <Shield className="h-3 w-3 mr-1" />
                    Admin
                  </Badge>
                ) : (
                  user?.roles?.slice(0, 2).map(role => (
                    <Badge key={role.id_rol} variant="secondary" className="text-xs">
                      {role.nombre_rol}
                    </Badge>
                  ))
                )}
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onLogout}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:ml-64">
        {/* Top bar */}
        <header className="bg-white shadow-sm border-b px-4 py-3 lg:px-6">
          <div className="flex items-center justify-between">
            <Button
              variant="ghost"
              size="sm"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-6 w-6" />
            </Button>
            <h1 className="text-xl font-semibold text-gray-900 capitalize">
              {menuItems.find(item => item.id === currentPage)?.label || 'Dashboard'}
            </h1>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}