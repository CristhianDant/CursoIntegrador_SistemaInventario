import { useState } from "react";
import { Monitor, Smartphone, Tablet, CheckCircle, XCircle, MoreHorizontal } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu";

interface Device {
  id: string;
  macAddress: string;
  deviceType: 'desktop' | 'tablet' | 'smartphone';
  deviceName: string;
  status: 'pending' | 'approved' | 'revoked';
  lastConnection: string;
  userAgent: string;
  location: string;
}

const mockDevices: Device[] = [
  {
    id: '1',
    macAddress: '00:1B:44:11:3A:B7',
    deviceType: 'desktop',
    deviceName: 'PC Mostrador Principal',
    status: 'approved',
    lastConnection: '2024-01-15 14:30',
    userAgent: 'Chrome 120.0.0.0 Windows',
    location: 'Área de Ventas'
  },
  {
    id: '2',
    macAddress: '02:42:AC:11:00:02',
    deviceType: 'tablet',
    deviceName: 'iPad Cocina',
    status: 'approved',
    lastConnection: '2024-01-15 13:45',
    userAgent: 'Safari 17.0 iOS',
    location: 'Área de Producción'
  },
  {
    id: '3',
    macAddress: '00:50:56:C0:00:01',
    deviceType: 'smartphone',
    deviceName: 'iPhone Supervisor',
    status: 'pending',
    lastConnection: '2024-01-15 12:15',
    userAgent: 'Safari 17.0 iOS',
    location: 'Oficina'
  },
  {
    id: '4',
    macAddress: '08:00:27:12:34:56',
    deviceType: 'desktop',
    deviceName: 'PC Inventario',
    status: 'revoked',
    lastConnection: '2024-01-10 09:20',
    userAgent: 'Chrome 119.0.0.0 Windows',
    location: 'Almacén'
  }
];

export function DeviceManager() {
  const [devices, setDevices] = useState<Device[]>(mockDevices);

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
      case 'approved':
        return <Badge className="bg-green-100 text-green-800">Aprobado</Badge>;
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800">Pendiente</Badge>;
      case 'revoked':
        return <Badge className="bg-red-100 text-red-800">Revocado</Badge>;
      default:
        return <Badge>Desconocido</Badge>;
    }
  };

  const handleApprove = (deviceId: string) => {
    setDevices(prev => 
      prev.map(device => 
        device.id === deviceId 
          ? { ...device, status: 'approved' as const }
          : device
      )
    );
  };

  const handleRevoke = (deviceId: string) => {
    setDevices(prev => 
      prev.map(device => 
        device.id === deviceId 
          ? { ...device, status: 'revoked' as const }
          : device
      )
    );
  };

  const approvedDevices = devices.filter(d => d.status === 'approved').length;
  const pendingDevices = devices.filter(d => d.status === 'pending').length;
  const revokedDevices = devices.filter(d => d.status === 'revoked').length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Gestión de Equipos</h1>
          <p className="text-gray-600">Administra los dispositivos conectados al sistema</p>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Dispositivos</p>
                <p className="text-2xl font-bold text-gray-900">{devices.length}</p>
              </div>
              <Monitor className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Aprobados</p>
                <p className="text-2xl font-bold text-green-600">{approvedDevices}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pendientes</p>
                <p className="text-2xl font-bold text-yellow-600">{pendingDevices}</p>
              </div>
              <XCircle className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Revocados</p>
                <p className="text-2xl font-bold text-red-600">{revokedDevices}</p>
              </div>
              <XCircle className="h-8 w-8 text-red-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Devices Table */}
      <Card>
        <CardHeader>
          <CardTitle>Dispositivos Registrados</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Dispositivo</TableHead>
                <TableHead>Dirección MAC</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead>Última Conexión</TableHead>
                <TableHead>Ubicación</TableHead>
                <TableHead>Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {devices.map((device) => {
                const DeviceIcon = getDeviceIcon(device.deviceType);
                return (
                  <TableRow key={device.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <DeviceIcon className="h-5 w-5 text-gray-500" />
                        <div>
                          <p className="font-medium text-gray-900">{device.deviceName}</p>
                          <p className="text-sm text-gray-500">{device.userAgent}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="font-mono text-sm">{device.macAddress}</TableCell>
                    <TableCell className="capitalize">{device.deviceType}</TableCell>
                    <TableCell>{getStatusBadge(device.status)}</TableCell>
                    <TableCell>{device.lastConnection}</TableCell>
                    <TableCell>{device.location}</TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {device.status !== 'approved' && (
                            <DropdownMenuItem
                              onClick={() => handleApprove(device.id)}
                              className="text-green-600"
                            >
                              <CheckCircle className="h-4 w-4 mr-2" />
                              Aprobar
                            </DropdownMenuItem>
                          )}
                          {device.status !== 'revoked' && (
                            <DropdownMenuItem
                              onClick={() => handleRevoke(device.id)}
                              className="text-red-600"
                            >
                              <XCircle className="h-4 w-4 mr-2" />
                              Revocar
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Security Notes */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-6">
          <h3 className="font-semibold text-blue-900 mb-2">Notas de Seguridad</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Solo aprueba dispositivos que reconozcas y que estén físicamente en tu establecimiento</li>
            <li>• Revoca inmediatamente cualquier dispositivo perdido, robado o no autorizado</li>
            <li>• La dirección MAC es única por dispositivo y permite identificación precisa</li>
            <li>• Los dispositivos pendientes no pueden acceder al sistema hasta ser aprobados</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}