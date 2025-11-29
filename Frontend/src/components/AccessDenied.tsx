import { ShieldX } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";

interface AccessDeniedProps {
  moduleName?: string;
}

export function AccessDenied({ moduleName }: AccessDeniedProps) {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Card className="w-full max-w-md text-center">
        <CardHeader>
          <div className="flex justify-center mb-4">
            <div className="p-4 bg-red-100 rounded-full">
              <ShieldX className="h-12 w-12 text-red-600" />
            </div>
          </div>
          <CardTitle className="text-2xl text-red-600">Acceso Denegado</CardTitle>
          <CardDescription className="text-base">
            No tienes permisos para acceder a este módulo
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {moduleName && (
            <p className="text-sm text-muted-foreground">
              Se requiere permiso del módulo: <strong>{moduleName}</strong>
            </p>
          )}
          <p className="text-sm text-muted-foreground">
            Contacta a tu administrador si necesitas acceso a esta sección.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
