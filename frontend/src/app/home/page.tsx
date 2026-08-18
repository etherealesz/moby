'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import {
  LuArrowRight,
  LuCamera,
  LuCheck,
  LuLayers,
  LuLeaf,
  LuMapPin,
  LuNavigation,
  LuRecycle,
  LuScanLine,
  LuTruck,
  LuUpload,
} from 'react-icons/lu';
import {
  Badge,
  Box,
  Button,
  Card,
  Container,
  Group,
  Paper,
  Progress,
  rem,
  SimpleGrid,
  Stack,
  Text,
  ThemeIcon,
  Title,
} from '@mantine/core';
import { PRIMARY, SECONDARY, TERTIARY } from '@/lib/constants/colors';

// ── Sample Waste Items for Interactive Preview ────────────────────────────
const SAMPLE_WASTES = [
  {
    id: 'plastic-bottle',
    name: 'Botol Plastik PET',
    category: 'Anorganik (Daur Ulang)',
    categoryColor: 'teal',
    confidence: 98.4,
    icon: '🧴',
    description:
      'Plastik jenis Polyethylene Terephthalate yang dapat didaur ulang menjadi serat tekstil atau wadah baru.',
    actionTip:
      'Bilas bersih, lepaskan tutup, dan pipihkan sebelum dibuang ke TPS/Bank Sampah.',
  },
  {
    id: 'apple-core',
    name: 'Sisa Buah & Sayur',
    category: 'Organik (Kompos)',
    categoryColor: 'green',
    confidence: 96.8,
    icon: '🍎',
    description:
      'Limbah organik basah yang mudah terurai dan sangat cocok untuk bahan pupuk kompos alami.',
    actionTip:
      'Pisahkan dari plastik, masukkan ke wadah tertutup atau lubang biopori.',
  },
  {
    id: 'cardboard-box',
    name: 'Kardus & Kertas Karton',
    category: 'Anorganik (Kertas/Karton)',
    categoryColor: 'blue',
    confidence: 97.2,
    icon: '📦',
    description:
      'Serat selulosa yang bernilai ekonomis untuk diolah kembali menjadi bubur kertas.',
    actionTip: 'Lipat rapi, jaga agar tetap kering dan tidak terkena minyak.',
  },
  {
    id: 'battery',
    name: 'Baterai Bekas',
    category: 'Limbah B3 (Berbahaya)',
    categoryColor: 'red',
    confidence: 99.1,
    icon: '🔋',
    description:
      'Mengandung logam berat berbahaya yang memerlukan penanganan khusus di drop point terpadu.',
    actionTip:
      'Jangan dibakar atau dibuang ke tempat sampah biasa. Salurkan ke TPS khusus B3.',
  },
];

export default function HomePage() {
  const [mounted, setMounted] = useState(false);
  const [selectedSample, setSelectedSample] = useState(0);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSelectSample = (idx: number) => {
    setIsScanning(true);
    setSelectedSample(idx);
    setTimeout(() => {
      setIsScanning(false);
    }, 350);
  };

  const currentWaste = SAMPLE_WASTES[selectedSample];

  if (!mounted) {
    return null;
  }

  return (
    <Box
      style={{
        backgroundColor: '#ffffff',
        minHeight: '100vh',
        color: '#1d2d35',
      }}
    >
      {/* ── TOP NAVBAR ────────────────────────────────────────────────── */}
      <Box
        component="header"
        style={{
          borderBottom: '1px solid #e0f4f6',
          backgroundColor: '#ffffff',
          position: 'sticky',
          top: 0,
          zIndex: 100,
          boxShadow: '0 2px 8px rgba(2, 109, 119, 0.04)',
        }}
      >
        <Container size="lg" h={64}>
          <Group justify="space-between" h="100%" align="center">
            {/* Brand Logo */}
            <Link
              href="/home"
              style={{ textDecoration: 'none', color: 'inherit' }}
            >
              <Group gap="xs" align="center">
                <Image
                  src="/images/logo.png"
                  alt="TrashNav Logo"
                  width={34}
                  height={34}
                  style={{ borderRadius: 8 }}
                />
                <Box>
                  <Title
                    order={3}
                    style={{
                      color: PRIMARY[500],
                      fontWeight: 800,
                      lineHeight: 1.1,
                    }}
                  >
                    TrashNav
                  </Title>
                  <Text size="xs" style={{ color: '#4a6572', lineHeight: 1 }}>
                    Sistem Pengelolaan Sampah
                  </Text>
                </Box>
              </Group>
            </Link>

            {/* Navigation Links */}
            <Group gap="xl" visibleFrom="sm">
              <Link href="/home" style={{ textDecoration: 'none' }}>
                <Text fw={700} style={{ color: PRIMARY[500], fontSize: 14 }}>
                  Beranda
                </Text>
              </Link>
              <a href="#klasifikasi" style={{ textDecoration: 'none' }}>
                <Text fw={500} style={{ color: '#4a6572', fontSize: 14 }}>
                  Klasifikasi Sampah
                </Text>
              </a>
              <Link href="/navigation" style={{ textDecoration: 'none' }}>
                <Text fw={500} style={{ color: '#4a6572', fontSize: 14 }}>
                  Navigasi Rute
                </Text>
              </Link>
              <a href="#fitur" style={{ textDecoration: 'none' }}>
                <Text fw={500} style={{ color: '#4a6572', fontSize: 14 }}>
                  Fitur Unggulan
                </Text>
              </a>
            </Group>

            {/* CTA Button */}
            <Group gap="xs">
              <Button
                component={Link}
                href="/navigation"
                color="brand"
                size="sm"
                radius="md"
                rightSection={<LuNavigation size={14} />}
                style={{
                  backgroundColor: PRIMARY[500],
                  fontWeight: 600,
                  boxShadow: '0 4px 12px rgba(2, 109, 119, 0.25)',
                }}
              >
                Peta Navigasi
              </Button>
            </Group>
          </Group>
        </Container>
      </Box>

      {/* ── HERO SECTION ──────────────────────────────────────────────── */}
      <Box
        style={{
          background:
            'radial-gradient(ellipse at top left, #e0f4f6 0%, #f4fbfb 45%, #ffffff 100%)',
          paddingTop: rem(52),
          paddingBottom: rem(80),
          borderBottom: '1px solid #e0f4f6',
        }}
      >
        <Container size="lg">
          <SimpleGrid
            cols={{ base: 1, md: 2 }}
            spacing={{ base: 40, md: 56 }}
            verticalSpacing={40}
          >
            {/* Left Hero Text */}
            <Stack justify="center" gap="lg">
              <Text
                size="xs"
                fw={700}
                style={{
                  color: PRIMARY[600],
                  textTransform: 'uppercase',
                  letterSpacing: '0.08em',
                }}
              >
                Platform Pengelolaan Sampah Terpadu
              </Text>

              <Title
                order={1}
                style={{
                  fontSize: 'clamp(2.1rem, 4vw, 2.85rem)',
                  fontWeight: 900,
                  color: '#1d2d35',
                  lineHeight: 1.15,
                  letterSpacing: '-0.02em',
                }}
              >
                Kenali Sampah,{'\n'}
                <Text span style={{ color: PRIMARY[500] }}>
                  Selamatkan Bumi
                </Text>
              </Title>

              <Text
                size="md"
                style={{ color: '#4a6572', lineHeight: 1.65, maxWidth: 520 }}
              >
                Aplikasi untuk klasifikasi citra sampah rumah tangga secara
                praktis, terintegrasi dengan penunjuk arah dan rute pengangkutan
                menuju tempat penampungan sampah terdekat.
              </Text>

              <Group gap="md" pt="xs">
                <Button
                  component="a"
                  href="#klasifikasi"
                  size="md"
                  radius="md"
                  color="brand"
                  leftSection={<LuCamera size={16} />}
                  style={{
                    backgroundColor: PRIMARY[500],
                    fontWeight: 700,
                    boxShadow: '0 4px 14px rgba(2, 109, 119, 0.3)',
                  }}
                >
                  Mulai Klasifikasi
                </Button>

                <Button
                  component={Link}
                  href="/navigation"
                  size="md"
                  radius="md"
                  variant="outline"
                  color="brand"
                  rightSection={<LuArrowRight size={15} />}
                  style={{
                    borderColor: PRIMARY[300],
                    color: PRIMARY[600],
                    fontWeight: 600,
                    backgroundColor: '#ffffff',
                  }}
                >
                  Buka Peta Rute
                </Button>
              </Group>

              {/* Key Highlights */}
              <Group gap="xl" pt="sm">
                <Group gap={6}>
                  <ThemeIcon
                    size={22}
                    radius="xl"
                    color="brand"
                    variant="light"
                  >
                    <LuScanLine size={13} />
                  </ThemeIcon>
                  <Text size="xs" fw={600} style={{ color: '#4a6572' }}>
                    Klasifikasi Citra Sampah
                  </Text>
                </Group>
                <Group gap={6}>
                  <ThemeIcon size={22} radius="xl" color="teal" variant="light">
                    <LuRecycle size={13} />
                  </ThemeIcon>
                  <Text size="xs" fw={600} style={{ color: '#4a6572' }}>
                    Panduan Pemilahan
                  </Text>
                </Group>
                <Group gap={6}>
                  <ThemeIcon size={22} radius="xl" color="cyan" variant="light">
                    <LuMapPin size={13} />
                  </ThemeIcon>
                  <Text size="xs" fw={600} style={{ color: '#4a6572' }}>
                    Navigasi Titik TPS
                  </Text>
                </Group>
              </Group>
            </Stack>

            {/* Right Hero: Image Classifier Showcase Card */}
            <Stack justify="center" align="center">
              <Card
                shadow="lg"
                p="lg"
                radius="lg"
                withBorder
                style={{
                  width: '100%',
                  maxWidth: 480,
                  backgroundColor: '#ffffff',
                  borderColor: '#dbeceb',
                  boxShadow: '0 16px 36px rgba(2, 109, 119, 0.1)',
                }}
              >
                {/* Classifier Header */}
                <Group justify="space-between" align="center" mb="sm">
                  <Group gap="xs">
                    <ThemeIcon
                      size={32}
                      radius="md"
                      style={{
                        backgroundColor: '#e0f4f6',
                        color: PRIMARY[500],
                      }}
                    >
                      <LuScanLine size={18} />
                    </ThemeIcon>
                    <Box>
                      <Text
                        size="xs"
                        fw={700}
                        style={{
                          color: PRIMARY[700],
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        Klasifikasi Citra Sampah
                      </Text>
                      <Text size="xs" c="dimmed" style={{ fontSize: 11 }}>
                        Identifikasi Jenis Limbah
                      </Text>
                    </Box>
                  </Group>
                  <Badge size="xs" color="teal" variant="light">
                    Siap Digunakan
                  </Badge>
                </Group>

                {/* Interactive Scan Area */}
                <Box
                  p="md"
                  mb="sm"
                  style={{
                    border: `2px dashed ${isScanning ? PRIMARY[400] : '#b3e3e9'}`,
                    borderRadius: 12,
                    backgroundColor: isScanning ? '#e0f4f6' : '#f8fdfc',
                    textAlign: 'center',
                    transition: 'all 0.3s ease',
                  }}
                >
                  <Group justify="center" gap="sm" mb={6}>
                    <Text style={{ fontSize: 36 }}>{currentWaste.icon}</Text>
                  </Group>

                  <Text size="sm" fw={700} style={{ color: '#1d2d35' }}>
                    {currentWaste.name}
                  </Text>

                  <Badge
                    size="sm"
                    color={currentWaste.categoryColor}
                    variant="filled"
                    mt={4}
                    mb="xs"
                  >
                    {currentWaste.category}
                  </Badge>

                  {/* Confidence Bar */}
                  <Box mt="xs" px="md">
                    <Group justify="space-between" mb={4}>
                      <Text size="xs" c="dimmed" style={{ fontSize: 10 }}>
                        Kecocokan Kategori
                      </Text>
                      <Text
                        size="xs"
                        fw={700}
                        style={{ color: PRIMARY[600], fontSize: 11 }}
                      >
                        {currentWaste.confidence}%
                      </Text>
                    </Group>
                    <Progress
                      value={currentWaste.confidence}
                      size="sm"
                      radius="xl"
                      color="brand"
                      animated={isScanning}
                    />
                  </Box>

                  {/* Eco Action Tip */}
                  <Paper
                    p="xs"
                    radius="sm"
                    mt="sm"
                    style={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e0f4f6',
                      textAlign: 'left',
                    }}
                  >
                    <Group gap={6} align="flex-start">
                      <LuCheck
                        size={14}
                        color={PRIMARY[500]}
                        style={{ marginTop: 2, flexShrink: 0 }}
                      />
                      <Text
                        size="xs"
                        style={{
                          color: '#4a6572',
                          fontSize: 11,
                          lineHeight: 1.4,
                        }}
                      >
                        {currentWaste.actionTip}
                      </Text>
                    </Group>
                  </Paper>
                </Box>

                {/* Sample Selector */}
                <div>
                  <Text
                    size="xs"
                    fw={600}
                    mb={6}
                    c="dimmed"
                    style={{ fontSize: 11 }}
                  >
                    Pilih Contoh Sampah:
                  </Text>
                  <SimpleGrid cols={4} spacing="xs">
                    {SAMPLE_WASTES.map((waste, idx) => (
                      <Button
                        key={waste.id}
                        size="xs"
                        variant={selectedSample === idx ? 'filled' : 'light'}
                        color="brand"
                        onClick={() => handleSelectSample(idx)}
                        styles={{
                          root: {
                            padding: '4px 6px',
                            height: 'auto',
                            fontSize: 11,
                            backgroundColor:
                              selectedSample === idx ? PRIMARY[500] : '#f0fbfb',
                          },
                        }}
                      >
                        {waste.icon} {waste.name.split(' ')[0]}
                      </Button>
                    ))}
                  </SimpleGrid>
                </div>

                {/* Action CTA */}
                <Button
                  component="a"
                  href="#klasifikasi"
                  fullWidth
                  size="sm"
                  radius="md"
                  mt="md"
                  color="brand"
                  leftSection={<LuUpload size={15} />}
                  style={{
                    backgroundColor: PRIMARY[500],
                    fontWeight: 600,
                  }}
                >
                  Buka Kamera & Unggah Gambar
                </Button>
              </Card>
            </Stack>
          </SimpleGrid>
        </Container>
      </Box>

      {/* ── SECTION: KLASIFIKASI CITRA SAMPAH ─────────────────────────── */}
      <Box id="klasifikasi" py={72} style={{ backgroundColor: '#ffffff' }}>
        <Container size="lg">
          <Stack align="center" gap="xs" mb={44}>
            <Text
              size="xs"
              fw={700}
              style={{
                color: PRIMARY[600],
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
              }}
            >
              Modul Klasifikasi Citra
            </Text>
            <Title
              order={2}
              ta="center"
              style={{ color: '#1d2d35', fontWeight: 800 }}
            >
              Deteksi & Klasifikasi Sampah
            </Title>
            <Text ta="center" size="sm" c="dimmed" style={{ maxWidth: 580 }}>
              Gunakan kamera perangkat atau unggah foto sampah rumah tangga
              untuk mendapatkan rekomendasi pemilahan dan tindakan daur ulang
              secara instan.
            </Text>
          </Stack>

          {/* Interactive Classification Workspace Container */}
          <Paper
            p="xl"
            radius="lg"
            withBorder
            style={{
              backgroundColor: '#f8fdfc',
              borderColor: '#dbeceb',
              maxWidth: 860,
              margin: '0 auto',
            }}
          >
            <SimpleGrid cols={{ base: 1, md: 2 }} spacing="xl">
              {/* Upload Dropzone Box */}
              <Box
                p="xl"
                style={{
                  border: `2px dashed ${PRIMARY[300]}`,
                  borderRadius: 14,
                  backgroundColor: '#ffffff',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textAlign: 'center',
                  minHeight: 260,
                }}
              >
                <ThemeIcon
                  size={52}
                  radius="xl"
                  style={{
                    backgroundColor: '#e0f4f6',
                    color: PRIMARY[500],
                    marginBottom: 14,
                  }}
                >
                  <LuCamera size={26} />
                </ThemeIcon>
                <Text
                  fw={700}
                  size="sm"
                  style={{ color: '#1d2d35', marginBottom: 4 }}
                >
                  Ambil Foto / Unggah Gambar Sampah
                </Text>
                <Text size="xs" c="dimmed" mb="md" style={{ maxWidth: 260 }}>
                  Format JPG, PNG, atau WEBP untuk memproses dan
                  mengidentifikasi kategori sampah.
                </Text>
                <Group gap="xs">
                  <Button
                    size="xs"
                    radius="md"
                    color="brand"
                    leftSection={<LuUpload size={13} />}
                    style={{ backgroundColor: PRIMARY[500] }}
                  >
                    Pilih File Gambar
                  </Button>
                </Group>
              </Box>

              {/* Classification Output Details */}
              <Stack justify="space-between">
                <div>
                  <Text
                    size="xs"
                    fw={700}
                    mb={8}
                    style={{
                      color: PRIMARY[700],
                      textTransform: 'uppercase',
                      letterSpacing: '0.05em',
                    }}
                  >
                    Hasil Identifikasi
                  </Text>

                  <Paper
                    p="md"
                    radius="md"
                    style={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e0f4f6',
                      marginBottom: 12,
                    }}
                  >
                    <Group justify="space-between" align="center" mb={6}>
                      <Group gap="xs">
                        <Text style={{ fontSize: 24 }}>
                          {currentWaste.icon}
                        </Text>
                        <Box>
                          <Text fw={700} size="sm" style={{ color: '#1d2d35' }}>
                            {currentWaste.name}
                          </Text>
                          <Text size="xs" c="dimmed" style={{ fontSize: 11 }}>
                            Kategori Terdeteksi
                          </Text>
                        </Box>
                      </Group>
                      <Badge color={currentWaste.categoryColor} variant="light">
                        {currentWaste.category}
                      </Badge>
                    </Group>

                    <Text
                      size="xs"
                      style={{
                        color: '#4a6572',
                        lineHeight: 1.5,
                        marginTop: 8,
                      }}
                    >
                      {currentWaste.description}
                    </Text>
                  </Paper>

                  <Paper
                    p="md"
                    radius="md"
                    style={{
                      backgroundColor: '#f0fbfb',
                      border: '1px solid #dbeceb',
                    }}
                  >
                    <Text
                      size="xs"
                      fw={700}
                      style={{ color: PRIMARY[700], marginBottom: 4 }}
                    >
                      💡 Langkah Penanganan:
                    </Text>
                    <Text
                      size="xs"
                      style={{ color: '#4a6572', lineHeight: 1.5 }}
                    >
                      {currentWaste.actionTip}
                    </Text>
                  </Paper>
                </div>

                <Button
                  component={Link}
                  href="/navigation"
                  fullWidth
                  size="sm"
                  radius="md"
                  color="brand"
                  rightSection={<LuNavigation size={14} />}
                  style={{
                    backgroundColor: PRIMARY[500],
                    fontWeight: 600,
                  }}
                >
                  Cari Rute Pengantaran ke TPS
                </Button>
              </Stack>
            </SimpleGrid>
          </Paper>
        </Container>
      </Box>

      {/* ── SECTION: FITUR UNGGULAN ───────────────────────────────────── */}
      <Box
        id="fitur"
        py={72}
        style={{ backgroundColor: '#f8fbfc', borderTop: '1px solid #e0f4f6' }}
      >
        <Container size="lg">
          <Stack align="center" gap="xs" mb={48}>
            <Text
              size="xs"
              fw={700}
              style={{
                color: PRIMARY[600],
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
              }}
            >
              Fitur Utama
            </Text>
            <Title
              order={2}
              ta="center"
              style={{ color: '#1d2d35', fontWeight: 800, fontSize: '1.85rem' }}
            >
              Fitur Unggulan TrashNav
            </Title>
            <Text ta="center" size="sm" c="dimmed" style={{ maxWidth: 580 }}>
              Solusi terintegrasi untuk mengenali sampah dan mengoptimalkan rute
              penjemputan menuju TPS secara efisien.
            </Text>
          </Stack>

          <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="lg">
            {/* Feature 1 */}
            <Paper
              p="xl"
              radius="md"
              withBorder
              style={{
                borderColor: '#e0f4f6',
                backgroundColor: '#ffffff',
              }}
            >
              <ThemeIcon
                size={48}
                radius="md"
                style={{
                  backgroundColor: '#e0f4f6',
                  color: PRIMARY[500],
                  marginBottom: 16,
                }}
              >
                <LuScanLine size={24} />
              </ThemeIcon>
              <Title
                order={4}
                style={{ color: '#1d2d35', fontWeight: 700, marginBottom: 8 }}
              >
                Klasifikasi Citra Sampah
              </Title>
              <Text size="xs" style={{ color: '#4a6572', lineHeight: 1.6 }}>
                Identifikasi jenis sampah organik, anorganik, B3, dan daur ulang
                secara otomatis dari foto kamera perangkat Anda.
              </Text>
            </Paper>

            {/* Feature 2 */}
            <Paper
              p="xl"
              radius="md"
              withBorder
              style={{
                borderColor: '#e0f4f6',
                backgroundColor: '#ffffff',
              }}
            >
              <ThemeIcon
                size={48}
                radius="md"
                style={{
                  backgroundColor: '#e8f5ee',
                  color: SECONDARY[500],
                  marginBottom: 16,
                }}
              >
                <LuMapPin size={24} />
              </ThemeIcon>
              <Title
                order={4}
                style={{ color: '#1d2d35', fontWeight: 700, marginBottom: 8 }}
              >
                Peta & Deteksi Lokasi GPS
              </Title>
              <Text size="xs" style={{ color: '#4a6572', lineHeight: 1.6 }}>
                Deteksi otomatis posisi penjemputan sampah dan kemudahan
                menandai lokasi TPS pada peta interaktif OpenStreetMap.
              </Text>
            </Paper>

            {/* Feature 3 */}
            <Paper
              p="xl"
              radius="md"
              withBorder
              style={{
                borderColor: '#e0f4f6',
                backgroundColor: '#ffffff',
              }}
            >
              <ThemeIcon
                size={48}
                radius="md"
                style={{
                  backgroundColor: '#fff8e1',
                  color: TERTIARY[600],
                  marginBottom: 16,
                }}
              >
                <LuTruck size={24} />
              </ThemeIcon>
              <Title
                order={4}
                style={{ color: '#1d2d35', fontWeight: 700, marginBottom: 8 }}
              >
                Multi-Mode Transportasi
              </Title>
              <Text size="xs" style={{ color: '#4a6572', lineHeight: 1.6 }}>
                Kustomisasi navigasi rute untuk petugas kebersihan pejalan kaki
                maupun armada truk pengangkut sampah.
              </Text>
            </Paper>
          </SimpleGrid>
        </Container>
      </Box>

      {/* ── FOOTER ────────────────────────────────────────────────────── */}
      <Box
        component="footer"
        py={32}
        style={{ backgroundColor: PRIMARY[600], color: '#ffffff' }}
      >
        <Container size="lg">
          <Group justify="space-between" align="center">
            <Group gap="xs">
              <Image
                src="/images/logo.png"
                alt="TrashNav"
                width={28}
                height={28}
                style={{ borderRadius: 6 }}
              />
              <Text size="sm" fw={700} style={{ color: '#ffffff' }}>
                TrashNav{' '}
                <Text span fw={400} opacity={0.85}>
                  Platform
                </Text>
              </Text>
            </Group>
            <Text size="xs" opacity={0.85}>
              &copy; 2026 TrashNav. All rights reserved.
            </Text>
          </Group>
        </Container>
      </Box>
    </Box>
  );
}
