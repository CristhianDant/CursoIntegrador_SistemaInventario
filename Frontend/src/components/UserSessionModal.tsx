import { useState } from "react";
import { Monitor, Smartphone, Tablet, MapPin, Clock, Shield, X } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";

interface UserSession {
  id: string;
  startTime: string;
  endTime?: string;
  duration: string;
  ipAddress: string;
  deviceType: 'desktop' | 'tablet' | 'smartphone';
  deviceName: string;
  location: string;
  userAgent: string;
  status: 'active' | 'ended';
  loginMethod: 'password' | '2fa';
}

interface UserSessionModalProps {
  isOpen: boolean;
  onClose: () => void;
  username: string;
}

const mockSessions: UserSession[] = [
  {
    id: '1',
    startTime: '2024-01-15 14:30:15',
    endTime: undefined,
    duration: '2h 15m',
    ipAddress: '192.168.1.105',
    deviceType: 'desktop',
    deviceName: 'PC Mostrador Principal',
    location: 'Área de Ventas',
    userAgent: 'Chrome 120.0.0.0 Windows 10',
    status: 'active',
    loginMethod: 'password'
  },
  {
    id: '2',
    startTime: '2024-01-15 08:00:00',
    endTime: '2024-01-15 14:30:00',
    duration: '6h 30m',
    ipAddress: '192.168.1.102',
    deviceType: 'tablet',
    deviceName: 'iPad Cocina',
    location: 'Área de Producción',
    userAgent: 'Safari 17.0 iOS 17.2',
    status: 'ended',
    loginMethod: '2fa'
  },
  {
    id: '3',
    startTime: '2024-01-14 16:45:30',
    endTime: '2024-01-14 18:30:00',
    duration: '1h 45m',
    ipAddress: '192.168.1.110',
    deviceType: 'smartphone',
    deviceName: 'iPhone Supervisor',
    location: 'Oficina',
    userAgent: 'Safari 17.0 iOS 17.2',
    status: 'ended',
    loginMethod: 'password'
  },
  {
    id: '4',
    startTime: '2024-01-14 09:15:00',
    endTime: '2024-01-14 15:00:00',
    duration: '5h 45m',
    ipAddress: '192.168.1.105',
    deviceType: 'desktop',
    deviceName: 'PC Mostrador Principal',
    location: 'Área de Ventas',
    userAgent: 'Chrome 119.0.0.0 Windows 10',
    status: 'ended',
    loginMethod: 'password'
  },
  {
    id: '5',
    startTime: '2024-01-13 14:20:00',
    endTime: '2024-01-13 17:45:00',
    duration: '3h 25m',
    ipAddress: '192.168.1.108',
    deviceType: 'tablet',
    deviceName: 'Samsung Galaxy Tab',
    location: 'Almacén',
    userAgent: 'Chrome 119.0.0.0 Android',
    status: 'ended',
    loginMethod: 'password'
  }
];

export function UserSessionModal({ isOpen, onClose, username }: UserSessionModalProps) {
  const [selectedTab, setSelectedTab] = useState("all");

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'desktop':
        return Monitor;
      case 'tablet':
        return Tablet;
      case 'smartphone':
        return Smartphone;
      default:
        return Monitor;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-100 text-green-800">Activa</Badge>;
      case 'ended':
        return <Badge className="bg-gray-100 text-gray-800">Finalizada</Badge>;
      default:
        return <Badge>Desconocido</Badge>;
    }
  };

  const getLoginMethodBadge = (method: string) => {
    switch (method) {
      case '2fa':
        return <Badge className="bg-blue-100 text-blue-800"><Shield className="h-3 w-3 mr-1" />2FA</Badge>;
      case 'password':
        return <Badge className="bg-gray-100 text-gray-800">Contraseña</Badge>;
      default:
        return <Badge>Desconocido</Badge>;
    }
  };

  const filteredSessions = selectedTab === "active" 
    ? mockSessions.filter(s => s.status === 'active')
    : selectedTab === "ended"
    ? mockSessions.filter(s => s.status === 'ended')
    : mockSessions;

  const activeSessions = mockSessions.filter(s => s.status === 'active').length;
  const totalSessions = mockSessions.length;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div>
              <DialogTitle className="text-xl">Historial de Sesiones</DialogTitle>
              <p className="text-sm text-gray-600 mt-1">Usuario: {username}</p>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600">Sesiones Activas</p>
                  <p className="text-2xl font-bold text-green-900">{activeSessions}</p>
                </div>
                <Shield className="h-8 w-8 text-green-600" />
              </div>
            </div>

            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-600">Total Sesiones</p>
                  <p className="text-2xl font-bold text-blue-900">{totalSessions}</p>
                </div>
                <Clock className="h-8 w-8 text-blue-600" />
              </div>
            </div>

            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-orange-600">Última Sesión</p>
                  <p className="text-sm font-bold text-orange-900">Hoy 14:30</p>
                </div>
                <MapPin className="h-8 w-8 text-orange-600" />
              </div>
            </div>

            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-600">Dispositivos</p>
                  <p className="text-2xl font-bold text-purple-900">3</p>
                </div>
                <Monitor className="h-8 w-8 text-purple-600" />
              </div>
            </div>
          </div>

          {/* Sessions Table */}
          <Tabs value={selectedTab} onValueChange={setSelectedTab}>
            <TabsList>
              <TabsTrigger value="all">Todas ({totalSessions})</TabsTrigger>
              <TabsTrigger value="active">Activas ({activeSessions})</TabsTrigger>
              <TabsTrigger value="ended">Finalizadas ({totalSessions - activeSessions})</TabsTrigger>
            </TabsList>

            <TabsContent value={selectedTab} className="mt-4">
              <div className="border rounded-lg max-h-96 overflow-y-auto">
                <Table>
                  <TableHeader className="sticky top-0 bg-white">
                    <TableRow>
                      <TableHead>Dispositivo</TableHead>
                      <TableHead>Inicio</TableHead>
                      <TableHead>Duración</TableHead>
                      <TableHead>IP</TableHead>
                      <TableHead>Ubicación</TableHead>
                      <TableHead>Método</TableHead>
                      <TableHead>Estado</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredSessions.map((session) => {
                      const DeviceIcon = getDeviceIcon(session.deviceType);
                      return (
                        <TableRow key={session.id}>
                          <TableCell>
                            <div className="flex items-center space-x-3">
                              <DeviceIcon className="h-4 w-4 text-gray-500" />
                              <div>
                                <p className="font-medium text-sm">{session.deviceName}</p>
                                <p className="text-xs text-gray-500">{session.userAgent}</p>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div>
                              <p className="text-sm">{session.startTime.split(' ')[0]}</p>
                              <p className="text-xs text-gray-500">{session.startTime.split(' ')[1]}</p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <p className="text-sm font-medium">{session.duration}</p>
                            {session.endTime && (
                              <p className="text-xs text-gray-500">Hasta {session.endTime.split(' ')[1]}</p>
                            )}
                          </TableCell>
                          <TableCell className="font-mono text-xs">{session.ipAddress}</TableCell>
                          <TableCell>
                            <div className="flex items-center space-x-1">
                              <MapPin className="h-3 w-3 text-gray-400" />
                              <span className="text-sm">{session.location}</span>
                            </div>
                          </TableCell>
                          <TableCell>{getLoginMethodBadge(session.loginMethod)}</TableCell>
                          <TableCell>{getStatusBadge(session.status)}</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </div>
            </TabsContent>
          </Tabs>

          {/* Security Info */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
              <Shield className="h-4 w-4 mr-2" />
              Información de Seguridad
            </h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Las sesiones activas se muestran en tiempo real</li>
              <li>• Cierra sesión inmediatamente si detectas actividad sospechosa</li>
              <li>• Las direcciones IP te ayudan a identificar ubicaciones de acceso</li>
              <li>• Se recomienda usar autenticación de dos factores (2FA) para mayor seguridad</li>
            </ul>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}