// Montu Manager MongoDB Initialization Script
// This script creates the initial database structure and indexes

// Switch to the montu_manager database
db = db.getSiblingDB('montu_manager');

// Create collections with validation schemas
db.createCollection('tasks', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'project', 'type', 'task', 'status', 'milestone'],
            properties: {
                _id: {
                    bsonType: 'string',
                    description: 'Task ID in format: ep01_seq0010_sh0010_lighting'
                },
                project: {
                    bsonType: 'string',
                    description: 'Project code (e.g., SWA)'
                },
                type: {
                    bsonType: 'string',
                    enum: ['shot', 'asset'],
                    description: 'Task type: shot or asset'
                },
                episode: {
                    bsonType: 'string',
                    description: 'Episode identifier'
                },
                sequence: {
                    bsonType: 'string',
                    description: 'Sequence identifier'
                },
                shot: {
                    bsonType: 'string',
                    description: 'Shot identifier'
                },
                task: {
                    bsonType: 'string',
                    description: 'Task type (lighting, composite, etc.)'
                },
                artist: {
                    bsonType: 'string',
                    description: 'Assigned artist name'
                },
                status: {
                    bsonType: 'string',
                    enum: ['not_started', 'in_progress', 'completed', 'on_hold', 'cancelled'],
                    description: 'Current task status'
                },
                milestone: {
                    bsonType: 'string',
                    enum: ['not_started', 'single_frame', 'low_quality', 'final_render', 'final_comp', 'approved'],
                    description: 'Current milestone'
                },
                priority: {
                    bsonType: 'string',
                    enum: ['low', 'medium', 'high', 'urgent'],
                    description: 'Task priority level'
                },
                frame_range: {
                    bsonType: 'object',
                    properties: {
                        start: { bsonType: 'int' },
                        end: { bsonType: 'int' }
                    },
                    description: 'Frame range for the task'
                }
            }
        }
    }
});

db.createCollection('project_configs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'name', 'base_path'],
            properties: {
                _id: {
                    bsonType: 'string',
                    description: 'Project code (e.g., SWA)'
                },
                name: {
                    bsonType: 'string',
                    description: 'Project full name'
                },
                base_path: {
                    bsonType: 'string',
                    description: 'Base project path'
                }
            }
        }
    }
});

db.createCollection('media_records', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['_id', 'linked_task_id', 'linked_version', 'author'],
            properties: {
                _id: {
                    bsonType: 'string',
                    description: 'Unique media record ID'
                },
                linked_task_id: {
                    bsonType: 'string',
                    description: 'Associated task ID'
                },
                linked_version: {
                    bsonType: 'string',
                    description: 'Associated version'
                }
            }
        }
    }
});

// Create indexes for performance
db.tasks.createIndex({ 'project': 1, 'episode': 1, 'sequence': 1, 'shot': 1 });
db.tasks.createIndex({ 'status': 1 });
db.tasks.createIndex({ 'priority': 1 });
db.tasks.createIndex({ 'artist': 1 });
db.tasks.createIndex({ 'task': 1 });

db.project_configs.createIndex({ 'name': 1 });

db.media_records.createIndex({ 'linked_task_id': 1 });
db.media_records.createIndex({ 'linked_version': 1 });

print('Montu Manager database initialized successfully!');
