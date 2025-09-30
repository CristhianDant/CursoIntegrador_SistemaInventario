import { ChefHat, CheckCircle, BarChart3, Shield, Clock, Smartphone } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent } from "./ui/card";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface LandingPageProps {
  onGetStarted: () => void;
}

export function LandingPage({ onGetStarted }: LandingPageProps) {
  const features = [
    {
      icon: BarChart3,
      title: "Control Total de Inventario",
      description: "Gestiona tus insumos con alertas automáticas de vencimiento y bajo stock"
    },
    {
      icon: CheckCircle,
      title: "Gestión de Recetas",
      description: "Organiza tus recetas y calcula automáticamente los costos de producción"
    },
    {
      icon: Clock,
      title: "Reportes en Tiempo Real",
      description: "Obtén métricas clave y reportes detallados para maximizar tus ganancias"
    },
    {
      icon: Shield,
      title: "Prevención de Merma",
      description: "Reduce desperdicios con nuestro sistema inteligente de promociones automáticas"
    },
    {
      icon: Smartphone,
      title: "Acceso Multi-dispositivo",
      description: "Trabaja desde cualquier lugar con nuestra plataforma responsive"
    }
  ];

  const testimonials = [
    {
      name: "María González",
      business: "Panadería La Dulce Tradición",
      quote: "DulceControl revolucionó mi negocio. Reduje la merma en un 40% y ahora tengo control total de mis costos."
    },
    {
      name: "Carlos Mendoza", 
      business: "Pastelería Artesanal El Horno",
      quote: "Gracias a las alertas automáticas, nunca más se me acabaron los ingredientes en plena producción."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <ChefHat className="h-8 w-8 text-orange-600" />
              <span className="text-2xl font-bold text-gray-900">DulceControl</span>
            </div>
            <Button onClick={onGetStarted} className="bg-orange-600 hover:bg-orange-700">
              Iniciar Sesión
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 mb-6">
                El Software de <span className="text-orange-600">Gestión Definitivo</span> para tu Panadería
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Optimiza tu inventario, reduce la merma y maximiza tus ganancias con DulceControl. 
                La solución integral diseñada especialmente para panaderías artesanales.
              </p>
              <div className="space-y-4 mb-8">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-700">Reduce la merma hasta 40%</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-700">Alertas automáticas de vencimiento</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span className="text-gray-700">Reportes detallados de rentabilidad</span>
                </div>
              </div>
              <Button 
                onClick={onGetStarted}
                size="lg" 
                className="bg-orange-600 hover:bg-orange-700 text-lg px-8 py-3"
              >
                Comenzar Ahora
              </Button>
            </div>
            <div className="relative">
              <ImageWithFallback
                src="https://images.unsplash.com/photo-1628697639527-e370a51de205?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhcnRpc2FuJTIwYmFrZXJ5JTIwYnJlYWQlMjBwYXN0cnl8ZW58MXx8fHwxNzU4NzQ0NTQ3fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                alt="Panadería artesanal con productos frescos"
                className="rounded-lg shadow-2xl w-full h-96 object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Todo lo que necesitas para gestionar tu panadería
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              DulceControl integra todas las herramientas esenciales para el éxito de tu negocio en una sola plataforma
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <Card key={index} className="border-0 shadow-md hover:shadow-lg transition-shadow">
                  <CardContent className="p-6 text-center">
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                      <Icon className="h-6 w-6 text-orange-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                    <p className="text-gray-600">{feature.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Interfaz intuitiva y fácil de usar
            </h2>
            <p className="text-xl text-gray-600">
              Diseñado por panaderos para panaderos. Sin complicaciones técnicas.
            </p>
          </div>
          <div className="relative">
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1748366465774-aaa2160fe78d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxtb2Rlcm4lMjBkYXNoYm9hcmQlMjBjb21wdXRlciUyMHNjcmVlbnxlbnwxfHx8fDE3NTg3NDQ1NTB8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
              alt="Dashboard moderno de gestión"
              className="rounded-lg shadow-2xl w-full h-96 lg:h-[500px] object-cover"
            />
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-orange-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl lg:text-4xl font-bold text-gray-900 mb-4">
              Lo que dicen nuestros clientes
            </h2>
          </div>
          
          <div className="grid md:grid-cols-2 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="border-0 shadow-md">
                <CardContent className="p-8">
                  <p className="text-lg text-gray-700 mb-6 italic">
                    "{testimonial.quote}"
                  </p>
                  <div>
                    <p className="font-semibold text-gray-900">{testimonial.name}</p>
                    <p className="text-orange-600">{testimonial.business}</p>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-orange-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl lg:text-4xl font-bold text-white mb-6">
            ¿Listo para revolucionar tu panadería?
          </h2>
          <p className="text-xl text-orange-100 mb-8">
            Únete a cientos de panaderos que ya optimizaron sus negocios con DulceControl
          </p>
          <Button 
            onClick={onGetStarted}
            size="lg" 
            variant="secondary"
            className="bg-white text-orange-600 hover:bg-gray-100 text-lg px-8 py-3"
          >
            Comenzar Prueba Gratuita
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center space-x-2 mb-8">
            <ChefHat className="h-8 w-8 text-orange-600" />
            <span className="text-2xl font-bold text-white">DulceControl</span>
          </div>
          <div className="text-center">
            <p>&copy; 2024 DulceControl. Optimizando panaderías artesanales.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}