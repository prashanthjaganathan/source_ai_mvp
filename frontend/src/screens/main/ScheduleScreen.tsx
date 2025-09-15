import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  RefreshControl,
  Switch,
  TextInput,
  Modal,
  ActivityIndicator,
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { useAuth } from '../../context/AuthContext';
import { schedulerService, Schedule } from '../../services/api';

const ScheduleScreen: React.FC = () => {
  const { user } = useAuth();
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<Schedule | null>(null);
  const [frequency, setFrequency] = useState('24');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [silentModeEnabled, setSilentModeEnabled] = useState(false);

  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = async () => {
    try {
      setIsLoading(true);
      const userSchedules = await schedulerService.getSchedules(user?.id?.toString());
      setSchedules(userSchedules);
    } catch (error) {
      Alert.alert('Error', 'Failed to load schedules');
    } finally {
      setIsLoading(false);
    }
  };

  const onRefresh = async () => {
    setIsRefreshing(true);
    await loadSchedules();
    setIsRefreshing(false);
  };

  const openCreateModal = () => {
    setEditingSchedule(null);
    setFrequency('24');
    setNotificationsEnabled(true);
    setSilentModeEnabled(false);
    setModalVisible(true);
  };

  const openEditModal = (schedule: Schedule) => {
    setEditingSchedule(schedule);
    setFrequency(schedule.frequency_hours.toString());
    setNotificationsEnabled(schedule.notifications_enabled);
    setSilentModeEnabled(schedule.silent_mode_enabled);
    setModalVisible(true);
  };

  const handleSaveSchedule = async () => {
    if (!user?.id) return;

    try {
      const scheduleData = {
        user_id: user.id.toString(),
        frequency_hours: parseInt(frequency),
        notifications_enabled: notificationsEnabled,
        silent_mode_enabled: silentModeEnabled,
      };

      if (editingSchedule) {
        await schedulerService.updateSchedule(editingSchedule.id, scheduleData);
        Alert.alert('Success', 'Schedule updated successfully');
      } else {
        await schedulerService.createSchedule(scheduleData);
        Alert.alert('Success', 'Schedule created successfully');
      }

      setModalVisible(false);
      await loadSchedules();
    } catch (error) {
      Alert.alert('Error', 'Failed to save schedule');
    }
  };

  const handleDeleteSchedule = (scheduleId: number) => {
    Alert.alert(
      'Delete Schedule',
      'Are you sure you want to delete this schedule?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await schedulerService.deleteSchedule(scheduleId);
              await loadSchedules();
            } catch (error) {
              Alert.alert('Error', 'Failed to delete schedule');
            }
          },
        },
      ]
    );
  };

  const handleToggleSchedule = async (schedule: Schedule) => {
    try {
      if (schedule.is_active) {
        await schedulerService.pauseSchedule(schedule.id);
      } else {
        await schedulerService.resumeSchedule(schedule.id);
      }
      await loadSchedules();
    } catch (error) {
      Alert.alert('Error', 'Failed to update schedule');
    }
  };

  const getFrequencyText = (hours: number) => {
    if (hours < 24) {
      return `Every ${hours} hour${hours > 1 ? 's' : ''}`;
    } else if (hours === 24) {
      return 'Daily';
    } else {
      const days = Math.floor(hours / 24);
      return `Every ${days} day${days > 1 ? 's' : ''}`;
    }
  };

  const renderScheduleCard = (schedule: Schedule) => (
    <View key={schedule.id} style={styles.scheduleCard}>
      <View style={styles.scheduleHeader}>
        <View style={styles.scheduleInfo}>
          <Text style={styles.scheduleTitle}>
            {getFrequencyText(schedule.frequency_hours)}
          </Text>
          <Text style={styles.scheduleSubtitle}>
            Triggered {schedule.trigger_count} times
          </Text>
        </View>
        <View style={styles.scheduleActions}>
          <Switch
            value={schedule.is_active}
            onValueChange={() => handleToggleSchedule(schedule)}
            trackColor={{ false: '#ccc', true: '#007AFF' }}
            thumbColor={schedule.is_active ? '#fff' : '#f4f3f4'}
          />
        </View>
      </View>

      <View style={styles.scheduleDetails}>
        <View style={styles.detailRow}>
          <Icon name="notifications" size={16} color="#666" />
          <Text style={styles.detailText}>
            Notifications: {schedule.notifications_enabled ? 'On' : 'Off'}
          </Text>
        </View>
        <View style={styles.detailRow}>
          <Icon name="volume-off" size={16} color="#666" />
          <Text style={styles.detailText}>
            Silent Mode: {schedule.silent_mode_enabled ? 'On' : 'Off'}
          </Text>
        </View>
        {schedule.last_triggered_at && (
          <View style={styles.detailRow}>
            <Icon name="schedule" size={16} color="#666" />
            <Text style={styles.detailText}>
              Last triggered: {new Date(schedule.last_triggered_at).toLocaleString()}
            </Text>
          </View>
        )}
      </View>

      <View style={styles.scheduleFooter}>
        <TouchableOpacity
          style={styles.actionButton}
          onPress={() => openEditModal(schedule)}
        >
          <Icon name="edit" size={16} color="#007AFF" />
          <Text style={styles.actionButtonText}>Edit</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.actionButton, styles.deleteButton]}
          onPress={() => handleDeleteSchedule(schedule.id)}
        >
          <Icon name="delete" size={16} color="#ff3b30" />
          <Text style={[styles.actionButtonText, styles.deleteButtonText]}>Delete</Text>
        </TouchableOpacity>
      </View>
    </View>
  );

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading schedules...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Photo Schedules</Text>
        <TouchableOpacity style={styles.addButton} onPress={openCreateModal}>
          <Icon name="add" size={24} color="#fff" />
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={onRefresh} />
        }
      >
        {schedules.length > 0 ? (
          schedules.map(renderScheduleCard)
        ) : (
          <View style={styles.emptyState}>
            <Icon name="schedule" size={64} color="#ccc" />
            <Text style={styles.emptyStateText}>No schedules yet</Text>
            <Text style={styles.emptyStateSubtext}>
              Create a schedule to automatically capture photos
            </Text>
            <TouchableOpacity style={styles.createButton} onPress={openCreateModal}>
              <Text style={styles.createButtonText}>Create Schedule</Text>
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>

      {/* Create/Edit Modal */}
      <Modal
        visible={modalVisible}
        transparent
        animationType="slide"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {editingSchedule ? 'Edit Schedule' : 'Create Schedule'}
              </Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Icon name="close" size={24} color="#666" />
              </TouchableOpacity>
            </View>

            <View style={styles.modalBody}>
              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Frequency (hours)</Text>
                <TextInput
                  style={styles.input}
                  value={frequency}
                  onChangeText={setFrequency}
                  keyboardType="numeric"
                  placeholder="24"
                />
              </View>

              <View style={styles.switchGroup}>
                <Text style={styles.switchLabel}>Enable Notifications</Text>
                <Switch
                  value={notificationsEnabled}
                  onValueChange={setNotificationsEnabled}
                  trackColor={{ false: '#ccc', true: '#007AFF' }}
                  thumbColor={notificationsEnabled ? '#fff' : '#f4f3f4'}
                />
              </View>

              <View style={styles.switchGroup}>
                <Text style={styles.switchLabel}>Silent Mode</Text>
                <Switch
                  value={silentModeEnabled}
                  onValueChange={setSilentModeEnabled}
                  trackColor={{ false: '#ccc', true: '#007AFF' }}
                  thumbColor={silentModeEnabled ? '#fff' : '#f4f3f4'}
                />
              </View>
            </View>

            <View style={styles.modalFooter}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.saveButton}
                onPress={handleSaveSchedule}
              >
                <Text style={styles.saveButtonText}>
                  {editingSchedule ? 'Update' : 'Create'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e5e9',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  addButton: {
    backgroundColor: '#007AFF',
    borderRadius: 20,
    width: 40,
    height: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: '#666',
  },
  scheduleCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  scheduleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  scheduleInfo: {
    flex: 1,
  },
  scheduleTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  scheduleSubtitle: {
    fontSize: 14,
    color: '#666',
    marginTop: 2,
  },
  scheduleActions: {
    marginLeft: 12,
  },
  scheduleDetails: {
    marginBottom: 16,
  },
  detailRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  detailText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 8,
  },
  scheduleFooter: {
    flexDirection: 'row',
    gap: 12,
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    borderRadius: 6,
    backgroundColor: '#f0f0f0',
    flex: 1,
    justifyContent: 'center',
  },
  actionButtonText: {
    fontSize: 14,
    color: '#007AFF',
    marginLeft: 4,
  },
  deleteButton: {
    backgroundColor: '#ffe6e6',
  },
  deleteButtonText: {
    color: '#ff3b30',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyStateText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#666',
    marginTop: 16,
  },
  emptyStateSubtext: {
    fontSize: 16,
    color: '#999',
    marginTop: 8,
    textAlign: 'center',
    marginBottom: 24,
  },
  createButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    width: '90%',
    backgroundColor: '#fff',
    borderRadius: 12,
    maxHeight: '80%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e1e5e9',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  modalBody: {
    padding: 20,
  },
  inputGroup: {
    marginBottom: 20,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#f8f9fa',
  },
  switchGroup: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  switchLabel: {
    fontSize: 16,
    color: '#333',
  },
  modalFooter: {
    flexDirection: 'row',
    padding: 20,
    gap: 12,
  },
  cancelButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  saveButton: {
    flex: 1,
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
    backgroundColor: '#007AFF',
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});

export default ScheduleScreen;
