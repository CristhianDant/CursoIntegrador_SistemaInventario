import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { API_BASE_URL } from "../constants";
// @ts-ignore: SVG module is handled by the bundler (svgr) and may not have TypeScript declarations
import MiLogo from './Img/Pasteleria.svg?react';


interface LoginFormProps {
  onLogin: (email: string) => void;
}

export function LoginForm({ onLogin }: LoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/v1/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        onLogin(email); // o data.user.email si el backend devuelve info
      } else {
        const errorData = await response.json();
        console.error('Error en login:', errorData);
        setError(errorData.message || 'Error en el login');
      }
    } catch (err) {
      console.error('Error de conexión con el servidor:', err);
      setError('Error de conexión con el servidor');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-amber-50 p-6">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center ">
          <div className="flex justify-center mb-4">
           <div className="p-6 bg-orange-100 rounded-full h-32 w-32 flex items-center justify-center">
            <div style={{ height: '120px', width: '120px' }}> 
                <MiLogo className="h-full w-full text-orange-100" />
            </div> 
        </div>
          </div>
          <CardTitle className="text-2xl">Pastelería Dulce Encanto</CardTitle>
          <CardDescription>
            Sistema de Gestión para Pastelerías
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="Ingrese su email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                placeholder="Ingrese su contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            {error && (
              <Alert className="border-red-200 bg-red-50">
                <AlertDescription className="text-red-700">
                  {error}
                </AlertDescription>
              </Alert>
            )}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Iniciando..." : "Iniciar Sesión"}
            </Button>
          </form>
         
        </CardContent>
      </Card>
    </div>
  );
}